"""
Master E2E Test Suite Runner for Omni-Oracle.
Target: omni_oracle_app/e2e_tests/run_e2e_tests.py
Executes all 95 E2E test cases across Tiers 1-5, prints formatted summary reports.
"""

import sys
import time
import pytest
from pathlib import Path

# Ensure backend directory is in sys.path
e2e_dir = Path(__file__).resolve().parent
backend_dir = e2e_dir.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def main():
    print("=" * 80)
    print("      OMNI-ORACLE OPAQUE-BOX E2E TEST SUITE RUNNER")
    print("=" * 80)

    tier_files = [
        ("Tier 1: Feature Coverage", e2e_dir / "test_tier1_feature_coverage.py"),
        ("Tier 2: Boundary Cases", e2e_dir / "test_tier2_boundary_cases.py"),
        ("Tier 3: Pairwise Integration", e2e_dir / "test_tier3_cross_feature.py"),
        ("Tier 4: Real-World Scenarios", e2e_dir / "test_tier4_real_world.py"),
        ("Tier 5: Backend Adversarial", e2e_dir / "test_tier5_backend_adversarial.py"),
        ("Tier 5: Frontend Integration Adversarial", e2e_dir / "test_tier5_frontend_integration_adversarial.py")
    ]

    start_time = time.time()
    results = {}
    total_exit_code = 0

    for name, filepath in tier_files:
        print(f"\n[RUNNING] {name} ({filepath.name})...")
        exit_code = pytest.main(["-v", str(filepath)])
        results[name] = exit_code
        if exit_code != 0:
            total_exit_code = exit_code

    elapsed = time.time() - start_time

    print("\n" + "=" * 80)
    print("                     E2E TEST SUMMARY REPORT")
    print("=" * 80)
    print(f"{'Tier Name':<35} | {'File':<30} | {'Status':<10}")
    print("-" * 80)

    for name, filepath in tier_files:
        status = "PASSED" if results[name] == 0 else "FAILED"
        print(f"{name:<35} | {filepath.name:<30} | {status:<10}")

    print("-" * 80)
    print(f"Total Execution Time: {elapsed:.2f} seconds")
    overall_status = "SUCCESS - ALL TESTS PASSED" if total_exit_code == 0 else "FAILED - SOME TESTS FAILED"
    print(f"Overall Result: {overall_status}")
    print("=" * 80)

    sys.exit(total_exit_code)


if __name__ == "__main__":
    main()
