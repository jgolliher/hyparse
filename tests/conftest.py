"""Pytest configuration and shared fixtures."""
import pytest
import os
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_hy3_file(fixtures_dir):
    """Return path to a sample .hy3 file."""
    # This will be created when we add fixtures
    return fixtures_dir / "sample_minimal.hy3"
