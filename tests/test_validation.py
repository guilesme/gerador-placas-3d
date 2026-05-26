import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT_DIR / "src" / "web"
sys.path.insert(0, str(WEB_DIR))

from validation import validate_text


class ValidateTextTests(unittest.TestCase):
    def test_valid_text_has_no_errors_or_warnings(self):
        errors, warnings = validate_text("Portaria Principal")

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_long_text_returns_warning(self):
        errors, warnings = validate_text("A" * 101)

        self.assertEqual(errors, [])
        self.assertTrue(warnings)

    def test_emoji_returns_blocking_error(self):
        errors, warnings = validate_text("Portaria 🚪")

        self.assertTrue(errors)
        self.assertEqual(warnings, [])

    def test_common_punctuation_is_allowed(self):
        errors, warnings = validate_text("Bloco A & B / Salao (Fundos)")

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
