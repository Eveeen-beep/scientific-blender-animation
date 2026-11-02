#!/usr/bin/env python3
"""Read-only PNG sequence audit. Requires Pillow; never renders or alters frames.

Exit codes: 0 = complete sequence with matching supplied provenance;
1 = completed audit with repair frames or unverified/mismatched provenance;
2 = invalid arguments, unsafe report destination, or a fatal I/O error.
Dark-frame flags are advisory and do not change structural validity or exit code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import string
import sys
import tempfile
import warnings


DARK_LUMA_THRESHOLD = 5.0  # 8-bit mean luminance; review hint, never a failure.
SCHEMA_VERSION = 1


def nonnegative_int(value: str) -> int:
    if not re.fullmatch(r"[0-9]+", value):
        raise argparse.ArgumentTypeError("must be a non-negative decimal integer")
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("integer is too large") from exc


def positive_int(value: str) -> int:
    number = nonnegative_int(value)
    if number == 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only, fully decoded PNG sequence audit using Pillow.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Safety and interpretation:
  The range is inclusive. The pattern must be a single filename with exactly one
  {frame}, {frame:d}, or decimal zero-padding field (for example {frame:04d}).
  Paths, traversal, conversion fields, and non-PNG output names are rejected.
  --expected-provenance and --recorded-provenance are JSON FILE paths. Each must
  contain a non-empty JSON object, in distinct files. Canonical JSON equality is required.
  Metadata authenticity and adequacy remain the caller's responsibility: include
  scene/content hash, relevant render settings, camera and software version.
  A match permits reuse of structurally valid frames while repairing other frames.
  No metadata, an absent partner, invalid JSON, or a mismatch makes safe_resume
  false. Structural validity alone is reported as reuse_unverified.
  Mean luminance below 5/255 is only flagged_for_review; dark frames remain valid
  and are never automatically added to repair_frames. Visual approval is separate.
  The report is JSON on stdout. --report also writes JSON via atomic replacement;
  its name must end in .json and its parent must already exist. Images and
  provenance files cannot be report targets.
  This program never renders, deletes, renames, or writes input frames.

Exit codes:
  0  All requested frames are structurally valid and supplied provenance matches.
  1  Audit completed; repair_frames is non-empty or provenance is not verified.
  2  Bad arguments, unsafe report target, missing Pillow, or fatal report I/O.
""",
    )
    parser.add_argument("--directory", required=True, type=Path, help="Existing PNG directory")
    parser.add_argument("--start", required=True, type=nonnegative_int, help="First frame (inclusive)")
    parser.add_argument("--end", required=True, type=nonnegative_int, help="Last frame (inclusive)")
    parser.add_argument("--width", required=True, type=positive_int, help="Expected pixel width")
    parser.add_argument("--height", required=True, type=positive_int, help="Expected pixel height")
    parser.add_argument("--pattern", default="frame_{frame:04d}.png", help="Filename pattern (default: %(default)s)")
    parser.add_argument("--report", type=Path, help="Optional JSON output file (atomic write)")
    parser.add_argument("--expected-provenance", type=Path, help="JSON file describing intended render provenance")
    parser.add_argument("--recorded-provenance", type=Path, help="JSON file recording provenance of existing frames")
    return parser


def validate_pattern(pattern: str, start: int, end: int) -> None:
    try:
        fields = list(string.Formatter().parse(pattern))
    except ValueError as exc:
        raise ValueError(f"invalid --pattern: {exc}") from exc
    placeholders = [(field, spec, conversion) for _, field, spec, conversion in fields if field is not None]
    if len(placeholders) != 1 or placeholders[0][0] != "frame":
        raise ValueError("--pattern must contain exactly one field named {frame}")
    _, spec, conversion = placeholders[0]
    if conversion is not None or not re.fullmatch(r"(?:d|0?[1-9][0-9]?d)?", spec):
        raise ValueError("--pattern accepts only {frame}, {frame:d}, or decimal padding up to 99 digits")
    # Check every generated name: e.g. COM0..COM10 has reserved names only inside.
    for frame in range(start, end + 1):
        name = pattern.format(frame=frame)
        if (
            not name
            or name in (".", "..")
            or re.search(r'[\x00-\x1f<>:"/\\|?*]', name)
            or PureWindowsPath(name).drive
            or Path(name).name != name
            or name.endswith((" ", "."))
            or name.startswith(" ")
            or len(name) > 255
            or Path(name).suffix.lower() != ".png"
        ):
            raise ValueError("--pattern must produce a safe PNG basename, never a path")
        stem = name.split(".", 1)[0].upper()
        if re.fullmatch(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])", stem):
            raise ValueError("--pattern uses a reserved filename")


def identical_file(a: Path, b: Path) -> bool:
    if os.path.normcase(str(a.resolve())) == os.path.normcase(str(b.resolve())):
        return True
    try:
        return os.path.samefile(a, b)
    except (FileNotFoundError, OSError):
        return False


def validate_report(path: Path, frame_paths: list[Path], provenance_paths: list[Path]) -> Path:
    if (
        re.search(r'[\x00-\x1f<>:"|?*]', path.name)
        or path.name.endswith((" ", "."))
        or re.fullmatch(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])", path.name.split(".", 1)[0].upper())
    ):
        raise ValueError("--report must have a safe regular filename, without alternate data streams or device names")
    # Restrict reports to JSON, including when the destination does not yet exist.
    if path.suffix.lower() != ".json":
        raise ValueError("--report must have a .json extension")
    if path.is_symlink():
        raise ValueError("--report cannot be a symbolic link")
    resolved = path.resolve()
    if not resolved.parent.is_dir():
        raise ValueError("--report parent directory must already exist")
    if resolved.exists() and not resolved.is_file():
        raise ValueError("--report must be a file, not a directory or special object")
    for protected in frame_paths + provenance_paths:
        if identical_file(resolved, protected):
            raise ValueError(f"--report would overwrite a protected input: {protected}")
    # Also protect existing PNG files outside the requested range in this directory.
    for protected in frame_paths[0].parent.iterdir():
        if protected.suffix.lower() == ".png" and identical_file(resolved, protected):
            raise ValueError(f"--report would overwrite an input PNG: {protected}")
    return resolved


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def read_provenance(path: Path) -> tuple[dict, str]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    if not isinstance(data, dict) or not data:
        raise ValueError("provenance must be a non-empty JSON object")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return data, hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def check_provenance(expected: Path | None, recorded: Path | None) -> dict:
    result = {
        "status": "reuse_unverified",
        "match": False,
        "expected_path": str(expected.resolve()) if expected else None,
        "recorded_path": str(recorded.resolve()) if recorded else None,
        "comparison": "exact canonical JSON equality; only supplied metadata is verified",
        "expected_sha256": None,
        "recorded_sha256": None,
        "errors": [],
    }
    if expected is None and recorded is None:
        result["reason"] = "Neither provenance file was supplied. Structural validity does not authorize reuse."
        return result
    if expected is None or recorded is None:
        result["reason"] = "Both expected and recorded provenance files are required to verify reuse."
        result["errors"].append("missing_expected_provenance" if expected is None else "missing_recorded_provenance")
        return result
    # Comparing one file to itself is not independent provenance evidence.
    if identical_file(expected, recorded):
        result["reason"] = "Expected and recorded provenance must be distinct files."
        result["errors"].append("same_provenance_file")
        return result
    for label, path in (("expected", expected), ("recorded", recorded)):
        try:
            _, digest = read_provenance(path)
            result[f"{label}_sha256"] = digest
        except (OSError, ValueError, UnicodeError, RecursionError) as exc:
            result["errors"].append(f"{label}: {type(exc).__name__}: {exc}")
    if result["errors"]:
        result["reason"] = "Provenance could not be read and validated."
    elif result["expected_sha256"] == result["recorded_sha256"]:
        result.update(status="matched", match=True, reason="Supplied expected and recorded provenance match.")
    else:
        result.update(status="mismatch", reason="Provenance differs. Existing frames must not be silently reused.")
    return result


def inspect_frame(frame: int, path: Path, directory: Path, size: tuple[int, int], Image, ImageStat) -> dict:
    result = {"frame": frame, "filename": path.name, "status": "missing", "structurally_valid": False, "flags": []}
    try:
        # No input symlinks are accepted: even an in-directory link can change targets.
        if path.is_symlink() or path.resolve().parent != directory:
            result.update(status="unsafe_path", error="Input symlinks or paths outside the chosen directory are not read.")
            return result
        file_stat = path.stat()
        result["bytes"] = file_stat.st_size
        if not stat.S_ISREG(file_stat.st_mode):
            result.update(status="not_regular_file", error="Expected a regular PNG file.")
            return result
        if file_stat.st_size == 0:
            result["status"] = "zero_byte"
            return result
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as png:
                if png.format != "PNG":
                    result.update(status="not_png", error="Filename is PNG but the decoded file format is not PNG.")
                    return result
                png.verify()  # Validate PNG chunk checksums before full pixel decoding.
            with Image.open(path) as png:
                actual_size = png.size
                result["size"] = list(actual_size)
                frame_count = getattr(png, "n_frames", 1)
                result["png_image_count"] = frame_count
                minimum_mean = 255.0
                for index in range(frame_count):
                    png.seek(index)
                    png.load()  # Full decoding; no header-only or thumbnail-only acceptance.
                    rgba = png.convert("RGBA")
                    # Composite alpha on black only for an advisory visual statistic.
                    background = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
                    background.alpha_composite(rgba)
                    luma = ImageStat.Stat(background.convert("L")).mean[0]
                    minimum_mean = min(minimum_mean, luma)
                result["mean_luminance_min_8bit"] = round(minimum_mean, 6)
                if minimum_mean < DARK_LUMA_THRESHOLD:
                    result["flags"].append("flagged_for_review")
                    result["review_reason"] = "low_mean_luminance; may be intentional darkness or transparency"
        # Detect a writer changing the file while it was audited.
        after = path.stat()
        if (file_stat.st_size, file_stat.st_mtime_ns, file_stat.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            result.update(status="changed_during_audit", error="File changed while being read; rerun after writing stops.")
        elif actual_size != size:
            result.update(status="wrong_size", expected_size=list(size))
        else:
            result.update(status="valid", structurally_valid=True)
    except FileNotFoundError:
        result["status"] = "missing"
    except (OSError, ValueError, SyntaxError, EOFError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        result.update(status="corrupt_or_unreadable", error=f"{type(exc).__name__}: {exc}")
    return result


def atomic_json_write(path: Path, payload: str) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
            temp_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            # Only our temporary report can be removed, never an input frame.
            try:
                temp_path.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.end < args.start:
            raise ValueError("--end must be greater than or equal to --start")
        validate_pattern(args.pattern, args.start, args.end)
        directory = args.directory.resolve(strict=True)
        if not directory.is_dir():
            raise ValueError("--directory must be an existing directory")
        frame_paths = [directory / args.pattern.format(frame=frame) for frame in range(args.start, args.end + 1)]
        provenance_paths = [path for path in (args.expected_provenance, args.recorded_provenance) if path is not None]
        report_path = validate_report(args.report, frame_paths, provenance_paths) if args.report else None
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    try:
        from PIL import Image, ImageFile, ImageStat
    except ImportError:
        print("error: Pillow is required; install it in this Python environment with: python -m pip install Pillow", file=sys.stderr)
        return 2
    ImageFile.LOAD_TRUNCATED_IMAGES = False
    provenance = check_provenance(args.expected_provenance, args.recorded_provenance)
    frames = [inspect_frame(frame, path, directory, (args.width, args.height), Image, ImageStat) for frame, path in zip(range(args.start, args.end + 1), frame_paths)]
    valid = [item["frame"] for item in frames if item["structurally_valid"]]
    repair = [item["frame"] for item in frames if not item["structurally_valid"]]
    missing = [item["frame"] for item in frames if item["status"] == "missing"]
    flagged = [item["frame"] for item in frames if "flagged_for_review" in item["flags"]]
    unsafe = [item["frame"] for item in frames if item["status"] in ("unsafe_path", "changed_during_audit")]
    safe_resume = provenance["match"] and not unsafe
    last_contiguous = None
    for item in frames:
        if not item["structurally_valid"]:
            break
        last_contiguous = item["frame"]
    exit_code = 0 if not repair and safe_resume else 1
    report = {
        "schema_version": SCHEMA_VERSION,
        "read_only": True,
        "directory": str(directory),
        "request": {"start": args.start, "end": args.end, "width": args.width, "height": args.height, "pattern": args.pattern},
        "structure_complete": not repair,
        "safe_resume": bool(safe_resume),
        "reuse_status": "provenance_matched" if safe_resume else ("provenance_mismatch" if provenance["status"] == "mismatch" else "reuse_unverified"),
        "safe_resume_definition": "Supplied provenance matches and no path/change hazard was found; structurally valid frames may be reused. Does not certify visual correctness.",
        "provenance": provenance,
        "last_contiguous_valid_frame": last_contiguous,
        "last_contiguous_valid_frame_definition": "Last structurally valid frame in the uninterrupted prefix beginning at start; null if start is invalid/missing.",
        "valid_frames": valid,
        "confirmed_reusable_frames": valid if safe_resume else [],
        "missing_frames": missing,
        "repair_frames": repair,
        "repair_frames_definition": "Structurally invalid or missing frames only. If safe_resume=false, this list alone is NOT a safe render-resume plan.",
        "flagged_for_review": flagged,
        "dark_frame_rule": {"threshold_mean_luminance_8bit": DARK_LUMA_THRESHOLD, "alpha_composited_on": "black", "effect": "advisory only; never automatically invalidates a frame"},
        "counts": {"requested": len(frames), "valid": len(valid), "missing": len(missing), "repair": len(repair), "flagged_for_review": len(flagged), "confirmed_reusable": len(valid) if safe_resume else 0},
        "frames": frames,
        "exit_code": exit_code,
        "exit_codes": {"0": "complete structure and matching provenance", "1": "audit completed; repair or reuse verification required", "2": "argument, unsafe output, dependency, or fatal report I/O error"},
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if report_path:
        try:
            atomic_json_write(report_path, payload)
        except OSError as exc:
            print(f"error: could not atomically write report: {exc}", file=sys.stderr)
            return 2
    try:
        sys.stdout.write(payload)
    except UnicodeEncodeError:
        # The JSON remains readable on legacy consoles without corrupting filenames.
        sys.stdout.write(json.dumps(report, ensure_ascii=True, indent=2, allow_nan=False) + "\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
