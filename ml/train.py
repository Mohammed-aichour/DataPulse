"""
DataPulse Machine Learning Training Runner
CLI Entrypoint: python -m ml.train

Trains the 3-Horizon anti-leakage models:
  - Scenario A: Early Intake (Weeks 0-4, zero grades)
  - Scenario B: Mid-Term (Month 3, includes G1)
  - Scenario C: Late-Stage (Month 7, includes G1 + G2 + delta)
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
parent_of_root = root_dir.parent
for p in [str(root_dir), str(parent_of_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from DataPulse.src.ingestion.dataset_loader import DatasetLoader
    from DataPulse.src.preprocessing.transformer import EducationalTransformer
    from DataPulse.src.ml.trainer import ModelTrainer
except ImportError:
    from src.ingestion.dataset_loader import DatasetLoader
    from src.preprocessing.transformer import EducationalTransformer
    from src.ml.trainer import ModelTrainer


def train():
    start_time = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    print("=" * 80)
    print("  DATAPULSE MACHINE LEARNING TRAINING: 3-HORIZON ANTI-LEAKAGE ARCHITECTURE")
    print(f"  Execution Started: {started_at}")
    print("=" * 80)

    print("\n[Step 1/3] Ingesting and transforming education datasets...")
    loader = DatasetLoader()
    df_mat, df_por, _ = loader.load_raw_datasets()
    transformer = EducationalTransformer()
    students_df, courses_df, records_df = transformer.transform(df_mat, df_por)
    print(f"  * Total Enrollment Records: {len(records_df)}")
    print(f"  * Unique Students:          {len(students_df)}")

    print("\n[Step 2/3] Preparing features and training multi-horizon models...")
    trainer = ModelTrainer()
    full_df = trainer.prepare_dataset(records_df, students_df)
    metadata = trainer.train_and_evaluate_all_scenarios(full_df)

    print("\n[Step 3/3] Training Summary and Performance Certification:")
    for sc_key, sc in metadata["scenarios"].items():
        best_clf = sc["best_classifier"]
        best_reg = sc["best_regressor"]
        clf_metrics = sc["classification"][best_clf]
        reg_metrics = sc["regression"][best_reg]
        print(f"\n  --- {sc['scenario_name'].upper()} ---")
        print(f"  Description:         {sc['description']}")
        print(f"  Features Utilized:   {len(sc['features_used'])} features")
        print(f"  Best Classifier:     {best_clf}")
        print(f"    - Accuracy:        {clf_metrics['accuracy']*100:.1f}%")
        print(f"    - ROC-AUC:         {clf_metrics['roc_auc']:.3f}")
        print(f"    - 5-Fold CV AUC:   {clf_metrics['cv_roc_auc_mean']*100:.1f}% (+/- {clf_metrics['cv_roc_auc_std']*100:.1f}%)")
        print(f"  Best Regressor:      {best_reg}")
        print(f"    - MAE:             {reg_metrics['mae']:.2f} pts (/20)")
        print(f"    - RMSE:            {reg_metrics['rmse']:.2f}")
        print(f"    - R2 Score:        {reg_metrics['r2']:.3f}")
        top_features = list(sc["feature_importance"].items())[:3]
        top_str = ", ".join([f"{k} ({v:.3f})" for k, v in top_features])
        print(f"  Top Drivers:         {top_str}")

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print(f"  TRAINING COMPLETED IN {elapsed}s | ARTIFACTS SAVED TO models_artifacts/")
    print("=" * 80)

    return metadata


if __name__ == "__main__":
    train()
