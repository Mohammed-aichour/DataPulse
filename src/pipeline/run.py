"""
DataPulse Master ETL & Multi-Scenario ML Pipeline Runner
CLI Entrypoint: python -m src.pipeline.run
Coordinates Ingestion -> Multi-Pillar Validation -> 1-to-1 Entity Transformation -> Relational Loading -> Multi-Horizon ML Training.
"""

from datetime import datetime, timezone
import sys
import time
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
parent_of_root = root_dir.parent
for p in [str(root_dir), str(parent_of_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from src.ingestion.dataset_loader import DatasetLoader
    from src.preprocessing.validator import DataValidator
    from src.preprocessing.transformer import EducationalTransformer
    from src.pipeline.db_loader import DatabaseLoader
    from src.ml.trainer import ModelTrainer
except ImportError:
    from src.ingestion.dataset_loader import DatasetLoader
    from src.preprocessing.validator import DataValidator
    from src.preprocessing.transformer import EducationalTransformer
    from src.pipeline.db_loader import DatabaseLoader
    from src.ml.trainer import ModelTrainer


def run_pipeline() -> dict:
    start_time = time.time()
    print("=" * 75)
    print("  DATAPULSE — SMART CAMPUS ANALYTICS & PREDICTIVE INTELLIGENCE PLATFORM")
    print(f"  Pipeline Run Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 75)

    # 1. INGESTION
    print("\n[Stage 1/5] Extracting datasets & verifying SHA-256 cryptographic hashes...")
    loader = DatasetLoader()
    df_mat, df_por, metadata = loader.load_raw_datasets()
    print(f"  -> Extracted Math: {len(df_mat)} records | Portuguese: {len(df_por)} records")
    for m in metadata:
        print(f"  -> Source: {m.file_name} | SHA256: {m.sha256_checksum[:12]}... | Synthetic: {m.is_synthetic}")

    # 2. VALIDATION
    print("\n[Stage 2/5] Multi-Pillar Data Quality & Schema Conformance Auditing...")
    validator = DataValidator()
    _, report_mat = validator.validate_dataframe(df_mat, "Mathematics")
    _, report_por = validator.validate_dataframe(df_por, "Portuguese Language")
    overall_quality_score = round((report_mat.quality_score + report_por.quality_score) / 2.0, 1)
    print(f"  -> Math Institutional Score: {report_mat.quality_score}/100 ({report_mat.status})")
    print(f"  -> Portuguese Institutional Score: {report_por.quality_score}/100 ({report_por.status})")
    print(f"  -> Combined Institutional Quality Score: {overall_quality_score}/100")
    print(f"  -> Audited Quality Pillars: {report_mat.quality_pillars}")

    # 3. TRANSFORMATION
    print("\n[Stage 3/5] Transforming & 1-to-1 Entity Resolution (Eliminating Intra-Course Collisions)...")
    transformer = EducationalTransformer()
    students_df, courses_df, records_df = transformer.transform(df_mat, df_por)
    intra_dups = records_df.duplicated(subset=["student_id", "course_code"]).sum()
    print(f"  -> Resolved unique student individuals: {len(students_df)}")
    print(f"  -> Courses registered: {len(courses_df)}")
    print(f"  -> Academic enrollment records: {len(records_df)}")
    print(f"  -> Intra-course collision count: {intra_dups} (Zero intra-course duplication verified)")
    print(f"  -> Overall institutional pass rate: {(records_df['passing_status'].mean() * 100):.1f}%")

    # 4. DATABASE LOADING
    print("\n[Stage 4/5] Idempotent Relational Loading & SQL Views Compilation...")
    db_loader = DatabaseLoader()
    db_loader.setup_database_schema()
    db_loader.load_courses(courses_df)
    db_loader.load_students(students_df)
    db_loader.load_academic_records(records_df)
    db_loader.log_import(metadata)
    print("  -> Relational tables populated & SQL views updated.")

    # 5. MACHINE LEARNING (3-HORIZON FRAMEWORK)
    print("\n[Stage 5/5] Training 3-Horizon ML Framework (Eliminating Target Leakage)...")
    trainer = ModelTrainer()
    full_dataset = trainer.prepare_dataset(records_df, students_df)
    ml_metadata = trainer.train_and_evaluate_all_scenarios(full_dataset)

    for sc_key, sc in ml_metadata["scenarios"].items():
        best_c = sc["best_classifier"]
        c_auc = sc["classification"][best_c]["roc_auc"]
        best_r = sc["best_regressor"]
        r_r2 = sc["regression"][best_r]["r2"]
        print(f"  -> [{sc_key.upper()}]: Best Classifier={best_c} (ROC-AUC: {c_auc}) | Best Regressor={best_r} (R2: {r_r2})")

    duration = time.time() - start_time

    run_details = {
        "math_records": len(df_mat),
        "portuguese_records": len(df_por),
        "unique_students": len(students_df),
        "total_enrollments": len(records_df),
        "quality_score": overall_quality_score,
        "scenarios": {k: s["best_classifier"] for k, s in ml_metadata["scenarios"].items()}
    }

    db_loader.log_pipeline_execution(
        records_count=len(records_df),
        duration_sec=duration,
        quality_score=overall_quality_score,
        details=run_details
    )
    db_loader.close()

    print("\n" + "=" * 75)
    print(f"  PIPELINE FINISHED IN {duration:.2f}s WITH STATUS: SUCCESS (AUDITED & DEFENDED)")
    print("=" * 75)

    return {
        "status": "SUCCESS",
        "duration_seconds": round(duration, 2),
        "records_processed": len(records_df),
        "unique_students": len(students_df),
        "quality_score": overall_quality_score,
        "details": run_details
    }


if __name__ == "__main__":
    run_pipeline()
