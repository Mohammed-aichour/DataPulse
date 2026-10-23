"""
DataPulse Database Initialization Script
Executes schema creation, table registration, and analytical view compilation.

Usage:
    python scripts/init_db.py
    python -m scripts.init_db
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
parent_of_root = root_dir.parent
for p in [str(root_dir), str(parent_of_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from database.connection import engine, init_db, SessionLocal
    from database.models import Base
except ImportError:
    from database.connection import engine, init_db, SessionLocal
    from database.models import Base


def initialize_database():
    print("=" * 70)
    print("  DATAPULSE DATABASE INITIALIZATION")
    print(f"  Target Engine: {engine.url}")
    print("=" * 70)

    print("\n[Step 1/2] Creating relational tables registered with SQLAlchemy Base...")
    init_db()
    print("  * Relational tables created/verified successfully.")

    print("\n[Step 2/2] Compiling analytical SQL views...")
    views_sql_path = root_dir / "database" / "sql" / "views.sql"
    if views_sql_path.exists():
        sql_content = views_sql_path.read_text(encoding="utf-8")
        # Split statements on semicolon
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
        db = SessionLocal()
        try:
            for stmt in statements:
                db.execute(text(stmt))
            db.commit()
            print(f"  * Compiled {len(statements)} analytical SQL views successfully.")
        except Exception as e:
            db.rollback()
            print(f"  ! Note on SQL view compilation: {e}")
        finally:
            db.close()
    else:
        print("  ! views.sql not found, skipping view compilation.")

    print("\n" + "=" * 70)
    print("  DATABASE INITIALIZATION COMPLETE & READY")
    print("=" * 70)


if __name__ == "__main__":
    initialize_database()
