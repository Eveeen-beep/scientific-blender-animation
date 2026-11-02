"""Portable CLI checks using only temporary, generated fixtures."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sequence_audit.py"


class SequenceAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sequence-audit-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.frames = self.base / "frames"
        self.frames.mkdir()
        for frame in range(1, 7):
            Image.new("RGB", (12, 8), (100, 160, 220)).save(self.frame(frame))
        self.metadata = {
            "scene_sha256": "fixture-scene-a",
            "camera": "fixture-camera",
            "settings": {"resolution": [12, 8], "samples": 32},
            "software": "fixture-renderer",
        }
        self.expected = self.base / "expected.json"
        self.recorded = self.base / "recorded.json"
        self.expected.write_text(json.dumps(self.metadata), encoding="utf-8")
        # Formatting and object-key ordering must not change provenance equality.
        self.recorded.write_text(
            json.dumps(self.metadata, sort_keys=True, indent=2), encoding="utf-8"
        )
        self.matched = [
            "--expected-provenance", str(self.expected),
            "--recorded-provenance", str(self.recorded),
        ]

    def frame(self, number):
        return self.frames / f"frame_{number:04d}.png"

    def snapshot(self, excluded=()):
        """Also catch created/deleted files; only requested reports may change."""
        return {
            path.relative_to(self.base): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.base.rglob("*")
            if path.is_file() and path not in excluded
        }

    def audit(self, *arguments, expected_code=0, allowed_outputs=()):
        before = self.snapshot(allowed_outputs)
        process = subprocess.run(
            [
                sys.executable, str(SCRIPT), "--directory", str(self.frames),
                "--start", "1", "--end", "6", "--width", "12", "--height", "8",
                *arguments,
            ],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1"}, timeout=30,
        )
        self.assertEqual(process.returncode, expected_code, process.stderr)
        self.assertEqual(self.snapshot(allowed_outputs), before, "Input files changed")
        if expected_code == 2:
            self.assertEqual(process.stdout, "")
            self.assertIn("error:", process.stderr)
            return None
        report = json.loads(process.stdout)
        self.assertTrue(report["read_only"])
        self.assertEqual(report["exit_code"], expected_code)
        return report

    def test_valid_sequence_and_canonical_provenance_allow_reuse(self):
        report = self.audit(*self.matched)
        self.assertTrue(report["structure_complete"])
        self.assertTrue(report["safe_resume"])
        self.assertEqual(report["valid_frames"], list(range(1, 7)))
        self.assertEqual(report["confirmed_reusable_frames"], list(range(1, 7)))
        self.assertEqual(report["repair_frames"], [])
        self.assertEqual(report["last_contiguous_valid_frame"], 6)
        self.assertEqual(report["provenance"]["status"], "matched")

    def test_requested_json_report_matches_stdout_and_leaves_no_temp_file(self):
        output = self.base / "report.json"
        # Sequence audit intentionally permits replacing an ordinary JSON report.
        output.write_text("old report", encoding="utf-8")
        report = self.audit(
            *self.matched, "--report", str(output), allowed_outputs=(output,)
        )
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), report)
        self.assertEqual(list(self.base.glob(".report.json.*.tmp")), [])

    def test_missing_corrupt_empty_wrong_size_and_dark_frames(self):
        self.frame(2).unlink()
        self.frame(3).write_bytes(self.frame(1).read_bytes()[:40])
        self.frame(4).write_bytes(b"")
        Image.new("RGB", (13, 8), "white").save(self.frame(5))
        Image.new("RGB", (12, 8), "black").save(self.frame(6))
        report = self.audit(*self.matched, expected_code=1)
        self.assertEqual(
            [item["status"] for item in report["frames"]],
            ["valid", "missing", "corrupt_or_unreadable", "zero_byte", "wrong_size", "valid"],
        )
        self.assertFalse(report["structure_complete"])
        self.assertTrue(report["safe_resume"])
        self.assertEqual(report["valid_frames"], [1, 6])
        self.assertEqual(report["confirmed_reusable_frames"], [1, 6])
        self.assertEqual(report["missing_frames"], [2])
        self.assertEqual(report["repair_frames"], [2, 3, 4, 5])
        self.assertEqual(report["flagged_for_review"], [6])
        self.assertEqual(report["last_contiguous_valid_frame"], 1)

    def test_darkness_is_advisory_and_does_not_change_success_exit_code(self):
        for frame in range(1, 7):
            Image.new("RGB", (12, 8), "black").save(self.frame(frame))
        report = self.audit(*self.matched)
        self.assertTrue(report["structure_complete"])
        self.assertEqual(report["repair_frames"], [])
        self.assertEqual(report["flagged_for_review"], list(range(1, 7)))
        self.assertEqual(report["confirmed_reusable_frames"], list(range(1, 7)))

    def test_changed_source_blocks_reuse_even_when_all_frames_are_valid(self):
        self.recorded.write_text(
            json.dumps({**self.metadata, "scene_sha256": "fixture-scene-b"}),
            encoding="utf-8",
        )
        report = self.audit(*self.matched, expected_code=1)
        self.assertTrue(report["structure_complete"])
        self.assertFalse(report["safe_resume"])
        self.assertEqual(report["reuse_status"], "provenance_mismatch")
        self.assertEqual(report["confirmed_reusable_frames"], [])
        self.assertEqual(report["repair_frames"], [])

    def test_missing_provenance_does_not_authorize_reuse(self):
        for arguments in (
            (),
            ("--expected-provenance", str(self.expected)),
            ("--recorded-provenance", str(self.recorded)),
        ):
            with self.subTest(arguments=arguments):
                report = self.audit(*arguments, expected_code=1)
                self.assertTrue(report["structure_complete"])
                self.assertFalse(report["safe_resume"])
                self.assertEqual(report["reuse_status"], "reuse_unverified")
                self.assertEqual(report["confirmed_reusable_frames"], [])

    def test_same_file_is_not_independent_provenance(self):
        report = self.audit(
            "--expected-provenance", str(self.expected),
            "--recorded-provenance", str(self.expected), expected_code=1,
        )
        self.assertFalse(report["safe_resume"])
        self.assertIn("same_provenance_file", report["provenance"]["errors"])

    def test_invalid_provenance_blocks_reuse(self):
        for contents in ("{}", "[]", '{"scene":"a","scene":"b"}', '{"x":NaN}', "{"):
            with self.subTest(contents=contents):
                self.recorded.write_text(contents, encoding="utf-8")
                report = self.audit(*self.matched, expected_code=1)
                self.assertFalse(report["safe_resume"])
                self.assertTrue(report["provenance"]["errors"])
                self.assertEqual(report["confirmed_reusable_frames"], [])
        self.recorded.unlink()
        report = self.audit(*self.matched, expected_code=1)
        self.assertFalse(report["safe_resume"])
        self.assertTrue(report["provenance"]["errors"])

    def test_truncated_pngs_are_not_accepted_from_headers(self):
        truncated = self.frame(1).read_bytes()[:-16]
        for frame in range(1, 7):
            self.frame(frame).write_bytes(truncated)
        report = self.audit(*self.matched, expected_code=1)
        self.assertEqual(report["valid_frames"], [])
        self.assertEqual(report["repair_frames"], list(range(1, 7)))
        self.assertIsNone(report["last_contiguous_valid_frame"])

    def test_crc_valid_but_undecodable_pixels_are_rejected(self):
        original = self.frame(1).read_bytes()
        modified = bytearray(original[:8])
        offset = 8
        while offset < len(original):
            length = struct.unpack(">I", original[offset:offset + 4])[0]
            kind = original[offset + 4:offset + 8]
            data = original[offset + 8:offset + 8 + length]
            if kind == b"IDAT":
                data = b"invalid zlib pixels"
            modified.extend(
                struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            )
            offset += 12 + length
        self.frame(1).write_bytes(modified)
        # PNG chunk verification passes, so the audit must actually decode pixels.
        with Image.open(self.frame(1)) as png:
            png.verify()
        report = self.audit(*self.matched, expected_code=1)
        self.assertEqual(report["frames"][0]["status"], "corrupt_or_unreadable")
        self.assertEqual(report["repair_frames"], [1])

    def test_non_png_content_is_rejected_even_with_png_filename(self):
        Image.new("RGB", (12, 8), "white").save(self.frame(1), format="JPEG")
        report = self.audit(*self.matched, expected_code=1)
        self.assertEqual(report["frames"][0]["status"], "not_png")
        self.assertEqual(report["repair_frames"], [1])

    def test_unsafe_patterns_are_rejected(self):
        for pattern in (
            "../frame_{frame:04d}.png", "..\\frame_{frame:04d}.png",
            "{frame.real}.png", "{frame!s}.png", "{frame}_{frame}.png",
            "frame_{frame:04d}.jpg", "frame_{frame:{frame}}.png",
            str(self.base / "frame_{frame:04d}.png"),
        ):
            with self.subTest(pattern=pattern):
                self.audit("--pattern", pattern, expected_code=2)
        self.audit("--start", "0", "--end", "10", "--pattern", "COM{frame}.png", expected_code=2)

    def test_invalid_ranges_and_dimensions_are_rejected(self):
        for arguments in (
            ("--end", "0"), ("--start", "-1"),
            ("--width", "0"), ("--height", "8.5"),
        ):
            with self.subTest(arguments=arguments):
                self.audit(*arguments, expected_code=2)

    def test_unsafe_report_destinations_are_rejected_without_changes(self):
        for destination in (
            self.frame(1), self.expected, self.recorded,
            self.base / "absent" / "report.json",
            self.base / "frame.png:report.json", self.base / "CON.json",
            self.base / "report.json ",
        ):
            with self.subTest(destination=destination.name):
                self.audit(*self.matched, "--report", str(destination), expected_code=2)
        for extension in ("blend", "mp4"):
            destination = self.base / f"existing.{extension}"
            destination.write_bytes(b"protected fixture")
            with self.subTest(extension=extension):
                self.audit(*self.matched, "--report", str(destination), expected_code=2)

    def test_help_explains_reuse_and_exit_codes(self):
        process = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("Exit codes:", process.stdout)
        self.assertIn("safe_resume", process.stdout)


if __name__ == "__main__":
    unittest.main()
