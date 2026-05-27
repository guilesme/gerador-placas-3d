import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT_DIR / "src" / "web"
sys.path.insert(0, str(WEB_DIR))

import plate_service


class PlateServiceTests(unittest.TestCase):
    def test_missing_blender_returns_friendly_error(self):
        with mock.patch.dict("os.environ", {"BLENDER_PATH": "C:/missing/blender.exe"}):
            with mock.patch("subprocess.run", side_effect=FileNotFoundError):
                success, filepath, message = plate_service.generate_plate("Teste", 20, "CENTER")

        self.assertFalse(success)
        self.assertIsNone(filepath)
        self.assertIn("Executavel do Blender nao encontrado", message)
        self.assertIn("BLENDER_PATH", message)

    def test_timeout_returns_friendly_error(self):
        with mock.patch("subprocess.run", side_effect=plate_service.subprocess.TimeoutExpired("blender", 120)):
            success, filepath, message = plate_service.generate_plate("Teste", 20, "CENTER")

        self.assertFalse(success)
        self.assertIsNone(filepath)
        self.assertIn("Tempo limite atingido", message)

    def test_nonzero_exit_returns_blender_logs(self):
        result = plate_service.subprocess.CompletedProcess(
            args=["blender"],
            returncode=1,
            stdout="stdout log",
            stderr="stderr log",
        )

        with mock.patch("subprocess.run", return_value=result):
            success, filepath, message = plate_service.generate_plate("Teste", 20, "CENTER")

        self.assertFalse(success)
        self.assertIsNone(filepath)
        self.assertIn("stderr log", message)
        self.assertIn("stdout log", message)

    def test_reduced_plate_height_is_passed_to_blender(self):
        result = plate_service.subprocess.CompletedProcess(
            args=["blender"],
            returncode=1,
            stdout="stdout log",
            stderr="stderr log",
        )

        with mock.patch("subprocess.run", return_value=result) as run:
            plate_service.generate_plate("Teste", 20, "CENTER", 128)

        cmd = run.call_args.args[0]
        self.assertEqual(cmd[-2:], ["CENTER", "128"])

    def test_get_blender_bin_uses_blender_path_env(self):
        with mock.patch.dict("os.environ", {"BLENDER_PATH": "C:/Blender/blender.exe"}):
            self.assertEqual(plate_service.get_blender_bin(), "C:/Blender/blender.exe")

    def test_get_blender_bin_uses_path_lookup(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with mock.patch("shutil.which", return_value="C:/Tools/blender.exe"):
                self.assertEqual(plate_service.get_blender_bin(), "C:/Tools/blender.exe")


if __name__ == "__main__":
    unittest.main()
