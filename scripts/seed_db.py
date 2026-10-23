"""
DataPulse Database Seed Script
Populates the database with real, authenticated educational data idempotently.

Usage:
    python scripts/seed_db.py
    python -m scripts.seed_db
"""

import sys
from pathlib import Path

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
parent_of_root = root_dir.parent
for p in [str(root_dir), str(parent_of_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from etl.run import run_etl


def seed():
    print("=" * 70)
    print("  DATAPULSE DATABASE SEEDING ROUTINE")
    print("=" * 70)
    print("Executing idempotent ETL seeding...")
    result = run_etl()
    print("\nDatabase seeded successfully:")
    print(f"  * Unique Students: {result['unique_students']}")
    print(f"  * Enrollments:     {result['records_processed']}")
    print(f"  * Quality Score:   {result['quality_score']}/100")


if __name__ == "__main__":
    seed()
