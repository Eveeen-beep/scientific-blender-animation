"""Optional real-Blender inventory smoke test in a disposable factory scene.

Does not open user projects, render frames, install plugins, or run agent apps.
Run separately from unittest with --blender and a new --report JSON path.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = """
import bpy, sys
from pathlib import Path
destination = Path(sys.argv[sys.argv.index('--') + 1])
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 24
scene.render.fps = 24
scene.render.resolution_x = 320
scene.render.resolution_y = 180
scene.render.resolution_percentage = 100
cube = bpy.data.objects['Cube']
cube.location.x = 0
cube.keyframe_insert(data_path='location', frame=1)
cube.location.x = 1
cube.keyframe_insert(data_path='location', frame=24)
scene.frame_set(1)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(destination))
"""


def run_blender(arguments):
    result = subprocess.run(arguments, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=120)
    if result.returncode != 0:
        raise RuntimeError("Blender failed:\n" + result.stdout[-3000:] + result.stderr[-3000:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    executable = args.blender.expanduser().resolve()
    output = args.report.expanduser().resolve()
    if not executable.is_file():
        parser.error("--blender must point to an existing executable")
    if output.suffix.lower() != ".json" or output.exists():
        parser.error("--report must be a new .json file")
    with tempfile.TemporaryDirectory(prefix="scientific blender smoke ") as temporary:
        directory = Path(temporary)
        fixture = directory / "create fixture.py"
        blend = directory / "sample.blend"
        inventory = directory / "inventory.json"
        fixture.write_text(FIXTURE, encoding="utf-8")
        run_blender([str(executable), "--background", "--factory-startup",
                     "--disable-autoexec", "--python-exit-code", "1",
                     "--python", str(fixture), "--", str(blend)])
        original_hash = hashlib.sha256(blend.read_bytes()).hexdigest()
        run_blender([str(executable), "--background", "--factory-startup",
                     "--disable-autoexec", str(blend), "--python-exit-code", "1",
                     "--python", str(ROOT / "scripts" / "inspect_blend.py"),
                     "--", "--output", str(inventory)])
        report = json.loads(inventory.read_text(encoding="utf-8"))
        assert report["mode"] == "inventory_only_no_save_no_render"
        assert report["frame_range"] == [1, 24]
        assert report["effective_fps"] == 24
        assert report["resolution"] == [320, 180]
        cube = next(o for o in report["objects"] if o["name"] == "Cube")
        assert cube["animation"] and cube["animation"]["action"]
        assert hashlib.sha256(blend.read_bytes()).hexdigest() == original_hash
        # Keep the summary portable: do not publish local user/binary/temp paths.
        summary = {
            "passed": True,
            "blender_version": report["blender_version"],
            "engine_reported_not_rendered": report["engine"],
            "python_version": sys.version.split()[0],
            "checks": ["disposable factory scene saved", "real inventory written",
                       "timeline/resolution reported", "animation entry reported",
                       "source blend SHA256 unchanged"],
            "rendered": False,
            "agent_host_installation_tested": False,
            "limitations": ["No render, animation frame sweep or scientific validation",
                            "No Claude Code or Cursor product integration tested"],
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
