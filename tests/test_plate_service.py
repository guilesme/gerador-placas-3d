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


if __name__ == "__main__":
    unittest.main()
