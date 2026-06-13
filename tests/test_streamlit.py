import ast
import json
import os

import pytest

STREAMLIT_DIR = "/Users/derrick/Projects/polis-ph/streamlit"


def _parse(path: str) -> None:
    """Raise SyntaxError if the file does not parse cleanly."""
    with open(path) as f:
        ast.parse(f.read(), filename=path)


# ── file existence & syntax ────────────────────────────────────────────────────

def test_app_exists_and_no_syntax_errors():
    path = os.path.join(STREAMLIT_DIR, "app.py")
    assert os.path.isfile(path)
    _parse(path)


def test_senate_page_exists():
    assert os.path.isfile(os.path.join(STREAMLIT_DIR, "pages", "1_senate.py"))


def test_party_list_page_exists():
    assert os.path.isfile(os.path.join(STREAMLIT_DIR, "pages", "2_party_list.py"))


def test_regional_breakdown_page_exists():
    assert os.path.isfile(os.path.join(STREAMLIT_DIR, "pages", "3_regional_breakdown.py"))


# ── GeoJSON integrity ──────────────────────────────────────────────────────────

def test_regions_json_exists_and_valid():
    path = os.path.join(STREAMLIT_DIR, "data", "regions.json")
    assert os.path.isfile(path)
    with open(path) as f:
        data = json.load(f)
    assert len(data["features"]) == 17


# ── utils.py static analysis ───────────────────────────────────────────────────

def test_utils_region_map_has_17_keys():
    path = os.path.join(STREAMLIT_DIR, "utils.py")
    assert os.path.isfile(path)
    with open(path) as f:
        tree = ast.parse(f.read(), filename=path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "REGION_MAP":
                    assert isinstance(node.value, ast.Dict), "REGION_MAP is not a dict literal"
                    assert len(node.value.keys) == 17
                    return

    pytest.fail("REGION_MAP not found in utils.py")
