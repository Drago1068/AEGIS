"""Phase 0 must contain no scoring, recommendation, prediction, or trading logic.

This check is intentionally structural (module file names, function/class definitions, and
FastAPI route paths under ``backend/src/aegis``) rather than a naive whole-repository text
grep. Documentation, comments, and docstrings are out of scope, so architecture prose that
legitimately discusses concepts like "scoring" or "recommendation" does not cause a false
failure. See ``docs/architecture/decisions/0001-phase-0-tooling.md``.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

BACKEND_SRC = Path(__file__).resolve().parents[1] / "src" / "aegis"

FORBIDDEN_MODULE_NAME_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"^scor(e|ing)s?$",
        r"^recommend(ation)?s?$",
        r"^predict(ion)?s?$",
        r"^trad(e|ing)s?$",
        r"^orders?$",
    ]
]

FORBIDDEN_IDENTIFIER_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"^score",
        r"^recommend",
        r"^predict",
        r"^place_order",
        r"^submit_order",
        r"^execute_trade",
    ]
]

FORBIDDEN_ROUTE_PREFIXES = ("/score", "/recommend", "/predict", "/order", "/trade")

ROUTE_DECORATOR_RE = re.compile(r"@\w+\.(get|post|put|patch|delete)\(\s*[\"']([^\"']+)[\"']")


def _source_files() -> list[Path]:
    assert BACKEND_SRC.is_dir(), f"expected backend source directory at {BACKEND_SRC}"
    return sorted(BACKEND_SRC.rglob("*.py"))


def test_backend_source_tree_exists() -> None:
    """Guard against a silently empty/misconfigured scan scope."""

    files = _source_files()
    assert files, f"no Python source files found under {BACKEND_SRC}"


def test_no_forbidden_module_names() -> None:
    violations = [
        str(path.relative_to(BACKEND_SRC))
        for path in _source_files()
        if any(pattern.match(path.stem) for pattern in FORBIDDEN_MODULE_NAME_PATTERNS)
    ]
    assert not violations, f"forbidden domain-logic module names found: {violations}"


def test_no_forbidden_definitions() -> None:
    violations: list[str] = []
    for path in _source_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) and any(
                pattern.match(node.name) for pattern in FORBIDDEN_IDENTIFIER_PATTERNS
            ):
                violations.append(f"{path.relative_to(BACKEND_SRC)}:{node.lineno} {node.name}")
    assert not violations, f"forbidden domain-logic definitions found: {violations}"


def test_no_forbidden_route_paths() -> None:
    violations: list[str] = []
    for path in _source_files():
        source = path.read_text(encoding="utf-8")
        for match in ROUTE_DECORATOR_RE.finditer(source):
            route_path = match.group(2)
            if route_path.startswith(FORBIDDEN_ROUTE_PREFIXES):
                violations.append(f"{path.relative_to(BACKEND_SRC)}: {route_path}")
    assert not violations, f"forbidden domain-logic routes found: {violations}"
