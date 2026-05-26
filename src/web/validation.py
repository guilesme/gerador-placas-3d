"""Validation helpers for user-provided plate text."""

import re

UNSUPPORTED_TEXT_CHARS = re.compile(r'[^\w\s\.,\-\!\?&\'":;/\(\)\u00C0-\u00FF]')


def validate_text(text):
    """Return blocking errors and non-blocking warnings for plate text."""
    errors = []
    warnings = []

    invalid_chars = sorted(set(UNSUPPORTED_TEXT_CHARS.findall(text)))
    if invalid_chars:
        chars = " ".join(repr(c) for c in invalid_chars)
        errors.append(f"Caracteres nao suportados detectados: {chars}")

    if len(text) > 100:
        warnings.append("Texto muito longo pode ficar ilegivel")

    return errors, warnings
