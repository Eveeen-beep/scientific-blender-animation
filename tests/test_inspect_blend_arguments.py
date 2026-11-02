"""Output guards with a bpy stub; no Blender runtime inventory is exercised."""

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inspect_blend.py"
GUARD_RUNNER = """
import runpy
import sys
import types

def fail_on_blender_access(name):
    raise AssertionError('Output refusal must precede Blender access: ' + name)

bpy = types.ModuleType('bpy')
bpy.__getattr__ = fail_on_blender_access
sys.modules['bpy'] = bpy
script, output = sys.argv[1:]
sys.argv = [script, '--', '--output', output]
runpy.run_path(script, run_name='__main__')
"""


class InspectBlendOutputGuardTests(unittest.TestCase):
    def assert_refused(self, output, message):
        process = subprocess.run(
            [sys.executable, "-c", GUARD_RUNNER, str(SCRIPT), str(output)],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1"}, timeout=30,
        )
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertEqual(process.stdout, "")
        self.assertIn(message, process.stderr)
        self.assertNotIn("AssertionError", process.stderr)

    def test_existing_json_report_is_refused_unchanged(self):
        with tempfile.TemporaryDirectory(prefix="inspect-output-test-") as temporary:
            output = Path(temporary) / "report.json"
            original = b'{"fixture":"existing report"}\n'
            output.write_bytes(original)
            self.assert_refused(output, "Report already exists")
            self.assertEqual(output.read_bytes(), original)
            self.assertEqual(list(Path(temporary).iterdir()), [output])

    def test_non_json_asset_is_refused_unchanged(self):
        with tempfile.TemporaryDirectory(prefix="inspect-output-test-") as temporary:
            output = Path(temporary) / "scene.blend"
            original = b"fixture only; not an actual Blender scene"
            output.write_bytes(original)
            self.assert_refused(output, "Output must be a new .json report")
            self.assertEqual(output.read_bytes(), original)

    def test_existing_directory_is_refused(self):
        with tempfile.TemporaryDirectory(prefix="inspect-output-test-") as temporary:
            output = Path(temporary) / "report.json"
            output.mkdir()
            self.assert_refused(output, "Report already exists")
            self.assertTrue(output.is_dir())
            self.assertEqual(list(output.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
