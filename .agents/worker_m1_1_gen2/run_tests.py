import pytest
import sys

if __name__ == "__main__":
    ret = pytest.main(["omni_oracle_app/backend/tests/test_thai_astrology.py", "-v"])
    sys.exit(ret)
