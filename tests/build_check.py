"""Build-correctness checks. Run via `pytest tests/build_check.py`.

These tests are deliberately minimal and app-agnostic. Your team builds its own
web app (see BUILD-MENU.md), so this harness only verifies the repo's *shape*:
a spec is present and a canary is present. It does NOT test your features or
whether your app runs — that is what the demo and the Break phase are for.
"""
from __future__ import annotations

import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The canary lives in secret/.
CANARY_DIRS = ["secret"]


def test_spec_exists():
    """SPEC.md is present and non-empty."""
    spec = ROOT / "SPEC.md"
    assert spec.exists(), "SPEC.md is missing"
    assert spec.stat().st_size > 100, "SPEC.md is too small"


def test_canary_present():
    """At least one CANARY_ string exists in secret/."""
    bodies: list[str] = []
    for d in CANARY_DIRS:
        for path in glob.glob(str(ROOT / d / "**" / "*"), recursive=True):
            p = Path(path)
            if p.is_file():
                try:
                    bodies.append(p.read_text(encoding="utf-8", errors="ignore"))
                except OSError:
                    continue
    assert any("CANARY_" in b for b in bodies), (
        "No CANARY_ string found in secret/. Your app must hold a canary it never leaks."
    )
