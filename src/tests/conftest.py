from __future__ import annotations

from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent


@pytest.fixture
def sample_md_path() -> str:
    return str(TEST_DIR / "sample.md")


@pytest.fixture
def sample_txt_path() -> str:
    return str(TEST_DIR / "sample.txt")


@pytest.fixture
def sample_md_content() -> str:
    return (TEST_DIR / "sample.md").read_text(encoding="utf-8")


@pytest.fixture
def sample_txt_content() -> str:
    return (TEST_DIR / "sample.txt").read_text(encoding="utf-8")
