"""
Shared Pytest Fixtures for Omni-Oracle E2E Test Suite.
Target: omni_oracle_app/e2e_tests/conftest.py
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Add backend path to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app import app as flask_app


@pytest.fixture
def app_client():
    """Instantiates Flask test client for opaque-box endpoint testing."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def valid_divine_payload():
    """Standard valid payload matching project contract for /api/divine."""
    return {
        "full_name": "Somchai Jaidee",
        "birth_date": "1992-05-15",
        "birth_time": "05:30",
        "birth_province": "Bangkok",
        "selected_tarot_cards": [0, 12, 25, 31, 44, 50, 61, 72, 5, 18]
    }


@pytest.fixture
def mock_lottery_file():
    """Absolute path to 24 historical draw records JSON."""
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "backend",
            "data",
            "lottery_results_past_1_year.json"
        )
    )
