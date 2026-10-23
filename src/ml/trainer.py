"""
DataPulse Machine Learning Pipeline — Multi-Scenario 3-Horizon Framework
Eliminates Target Leakage by defining 3 distinct prediction horizons:
- Scenario A: Early Intake (Pre-Grades)
- Scenario B: Mid-Term (Post-Period 1 with G1)
- Scenario C: Late-Stage (Post-Period 2 with G1 and G2)
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score,
    mean_absolute_error, mean_squared_error, precision_score,
    r2_score, recall_score, roc_auc_score
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class ScenarioMetrics:
    scenario_name: str
    description: str
    features_used: List[str]
    best_classifier: str
    best_regressor: str
    classification: Dict[str, Any]
    regression: Dict[str, Any]
    feature_importance: Dict[str, float]


class ModelTrainer:
    CATEGORICAL_FEATURES = [
        "school", "sex", "address", "famsize", "Pstatus",
        "Mjob", "Fjob", "reason", "guardian", "schoolsup",
        "famsup", "paid", "activities", "nursery", "higher",
        "internet", "romantic", "course_code"
    ]

    BASE_NUMERICAL_FEATURES = [
        "age", "Medu", "Fedu", "traveltime", "studytime",
        "failures", "famrel", "freetime", "goout", "Dalc",
        "Walc", "health", "absences",
        "parent_edu_avg", "alcohol_index", "study_to_social_ratio"
    ]

    SCENARIO_DEFINITIONS = {
        "scenario_a": {
            "name": "Scenario A — Early Intake Risk Warning",
            "description": "Pre-term orientation prediction using only demographic, family, lifestyle, and past academic history. Zero grade information used.",
            "numerical": BASE_NUMERICAL_FEATURES,
        },
        "scenario_b": {
            "name": "Scenario B — Mid-Term Evaluation",
            "description": "Mid-semester prediction after Period 1 exam results (G1) are published.",
            "numerical": BASE_NUMERICAL_FEATURES + ["G1"],
        },
        "scenario_c": {
            "name": "Scenario C — Late-Stage Forecasting",
            "description": "End-of-term final projection after Period 1 and Period 2 exams (G1 & G2) and grade trajectory are published.",
            "numerical": BASE_NUMERICAL_FEATURES + ["G1", "G2", "grade_delta"],
        }
    }

    def __init__(self, artifacts_dir: Optional[str] = None):
        if artifacts_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.artifacts_dir = base_dir / "models_artifacts"
            self.reports_dir = base_dir / "reports" / "model_evaluation"
        else:
            self.artifacts_dir = Path(artifacts_dir)
            self.reports_dir = self.artifacts_dir / "reports"

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def prepare_dataset(self, df_records: pd.DataFrame, df_students: pd.DataFrame) -> pd.DataFrame:
        """Merge academic records with student demographic features."""
        merged = pd.merge(
            df_records,
            df_students,
            on="student_id",
            how="inner",
            suffixes=("", "_stu")
        )
        return merged

    def _train_scenario(
        self,
        full_df: pd.DataFrame,
        num_cols: List[str],
        scenario_key: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, float], Any, Any]:
        feature_cols = self.CATEGORICAL_FEATURES + num_cols
        X = full_df[feature_cols].copy()

        y_class = full_df["academic_risk"].values
        y_reg = full_df["G3"].values

        X_train, X_test, y_train_cls, y_test_cls, y_train_reg, y_test_reg = train_test_split(
            X, y_class, y_reg, test_size=0.20, random_state=42, stratify=y_class
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.CATEGORICAL_FEATURES)
            ]
        )

        # 1. Classification Models
        cls_candidates = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
            "Random Forest Classifier": RandomForestClassifier(n_estimators=120, max_depth=7, random_state=42),
            "Gradient Boosting Classifier": GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42)
        }

        best_cls_name = None
        best_cls_score = -1.0
        best_cls_pipe = None
        cls_results = {}

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        for name, clf in cls_candidates.items():
            pipe = Pipeline([
                ("preprocessor", preprocessor),
                ("classifier", clf)
            ])

            cv_scores = cross_val_score(pipe, X_train, y_train_cls, cv=cv, scoring="roc_auc")
            pipe.fit(X_train, y_train_cls)

            y_pred = pipe.predict(X_test)
            y_proba = pipe.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else y_pred

            acc = float(accuracy_score(y_test_cls, y_pred))
            prec = float(precision_score(y_test_cls, y_pred, zero_division=0))
            rec = float(recall_score(y_test_cls, y_pred, zero_division=0))
            f1 = float(f1_score(y_test_cls, y_pred, zero_division=0))
            auc = float(roc_auc_score(y_test_cls, y_proba))
            cm = confusion_matrix(y_test_cls, y_pred).tolist()

            cls_results[name] = {
                "model_name": name,
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "roc_auc": round(auc, 4),
                "cv_roc_auc_mean": round(float(cv_scores.mean()), 4),
                "cv_roc_auc_std": round(float(cv_scores.std()), 4),
                "confusion_matrix": cm
            }

            # Optimize for ROC-AUC / F1
            if auc > best_cls_score:
                best_cls_score = auc
                best_cls_name = name
                best_cls_pipe = pipe

        # 2. Regression Models
        reg_candidates = {
            "Ridge Regression": Ridge(alpha=1.0, random_state=42),
            "Random Forest Regressor": RandomForestRegressor(n_estimators=120, max_depth=7, random_state=42),
            "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42)
        }

        best_reg_name = None
        best_reg_r2 = -999.0
        best_reg_pipe = None
        reg_results = {}

        for name, reg in reg_candidates.items():
            pipe = Pipeline([
                ("preprocessor", preprocessor),
                ("regressor", reg)
            ])

            pipe.fit(X_train, y_train_reg)
            y_pred_reg = pipe.predict(X_test)

            mae = float(mean_absolute_error(y_test_reg, y_pred_reg))
            rmse = float(np.sqrt(mean_squared_error(y_test_reg, y_pred_reg)))
            r2 = float(r2_score(y_test_reg, y_pred_reg))

            reg_results[name] = {
                "model_name": name,
                "mae": round(mae, 4),
                "rmse": round(rmse, 4),
                "r2": round(r2, 4)
            }

            if r2 > best_reg_r2:
                best_reg_r2 = r2
                best_reg_name = name
                best_reg_pipe = pipe

        # 3. Feature Importance
        feature_importance_dict = {}
        try:
            fitted_prep = best_cls_pipe.named_steps["preprocessor"]
            cat_encoder = fitted_prep.named_transformers_["cat"]
            encoded_cat_names = list(cat_encoder.get_feature_names_out(self.CATEGORICAL_FEATURES))
            all_feature_names = num_cols + encoded_cat_names

            clf_model = best_cls_pipe.named_steps["classifier"]
            if hasattr(clf_model, "feature_importances_"):
                importances = clf_model.feature_importances_
            elif hasattr(clf_model, "coef_"):
                importances = np.abs(clf_model.coef_[0])
            else:
                importances = np.ones(len(all_feature_names))

            fi_series = pd.Series(importances, index=all_feature_names).sort_values(ascending=False)
            for f_name, val in fi_series.head(10).items():
                feature_importance_dict[f_name] = round(float(val), 4)
        except Exception as e:
            print(f"[ModelTrainer] Feature importance notice for {scenario_key}: {e}")

        # Persist scenario artifacts
        joblib.dump(best_cls_pipe, self.artifacts_dir / f"best_risk_classifier_{scenario_key}.joblib")
        joblib.dump(best_reg_pipe, self.artifacts_dir / f"best_grade_regressor_{scenario_key}.joblib")

        return cls_results, reg_results, feature_importance_dict, best_cls_pipe, best_reg_pipe

    def train_and_evaluate_all_scenarios(self, full_df: pd.DataFrame) -> Dict[str, Any]:
        """Trains models across all 3 horizons, benchmarks them, and writes unified report."""
        all_scenarios_results = {}

        for key, sc_def in self.SCENARIO_DEFINITIONS.items():
            cls_res, reg_res, fi, best_cls, best_reg = self._train_scenario(
                full_df=full_df,
                num_cols=sc_def["numerical"],
                scenario_key=key
            )

            best_cls_name = max(cls_res.items(), key=lambda x: x[1]["roc_auc"])[0]
            best_reg_name = max(reg_res.items(), key=lambda x: x[1]["r2"])[0]

            scenario_obj = ScenarioMetrics(
                scenario_name=sc_def["name"],
                description=sc_def["description"],
                features_used=self.CATEGORICAL_FEATURES + sc_def["numerical"],
                best_classifier=best_cls_name,
                best_regressor=best_reg_name,
                classification=cls_res,
                regression=reg_res,
                feature_importance=fi
            )
            all_scenarios_results[key] = asdict(scenario_obj)

            # Default alias points to Scenario C (Late Stage)
            if key == "scenario_c":
                joblib.dump(best_cls, self.artifacts_dir / "best_risk_classifier.joblib")
                joblib.dump(best_reg, self.artifacts_dir / "best_grade_regressor.joblib")

        # Unified Metadata
        metadata = {
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "framework": "3-Horizon Multi-Scenario Anti-Leakage Framework",
            "active_default_scenario": "scenario_c",
            "scenarios": all_scenarios_results,
            # Backward compatibility aliases
            "best_classifier": all_scenarios_results["scenario_c"]["best_classifier"],
            "best_regressor": all_scenarios_results["scenario_c"]["best_regressor"],
            "classification_metrics": all_scenarios_results["scenario_c"]["classification"],
            "regression_metrics": all_scenarios_results["scenario_c"]["regression"],
            "feature_importance": all_scenarios_results["scenario_c"]["feature_importance"],
            "train_samples": int(len(full_df) * 0.8),
            "test_samples": int(len(full_df) * 0.2),
        }

        with open(self.artifacts_dir / "model_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        self._write_comprehensive_report(metadata)
        return metadata

    def _write_comprehensive_report(self, metadata: dict):
        md_path = self.reports_dir / "model_evaluation_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# DataPulse — Multi-Scenario Machine Learning Evaluation Report\n\n")
            f.write(f"- **Trained At**: `{metadata['trained_at']}`\n")
            f.write(f"- **Methodological Architecture**: `{metadata['framework']}`\n")
            f.write(f"- **Dataset Split**: {metadata['train_samples']} Training records / {metadata['test_samples']} Unseen Test records (80/20 Stratified)\n\n")

            f.write("## 1. Multi-Horizon Predictive Benchmarks (Anti-Target Leakage)\n\n")
            f.write("To guarantee rigorous academic and production standards, models are evaluated across 3 distinct time horizons:\n\n")

            for sc_key, sc in metadata["scenarios"].items():
                f.write(f"### {sc['scenario_name']}\n")
                f.write(f"*{sc['description']}*\n\n")

                f.write("**Classification Comparison (Target: Academic Risk G3 < 10):**\n\n")
                f.write("| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 5-Fold CV ROC-AUC |\n")
                f.write("|---|---|---|---|---|---|---|\n")
                for m_name, m in sc["classification"].items():
                    f.write(
                        f"| {m_name} | {m['accuracy']*100:.1f}% | {m['precision']*100:.1f}% | "
                        f"{m['recall']*100:.1f}% | {m['f1_score']:.3f} | **{m['roc_auc']:.3f}** | "
                        f"{m['cv_roc_auc_mean']*100:.1f}% (±{m['cv_roc_auc_std']*100:.1f}%) |\n"
                    )

                f.write("\n**Regression Comparison (Target: Final Grade G3 [0-20]):**\n\n")
                f.write("| Model Name | MAE (Grade pts) | RMSE | R² Score |\n")
                f.write("|---|---|---|---|\n")
                for m_name, m in sc["regression"].items():
                    f.write(f"| {m_name} | {m['mae']:.2f} pts | {m['rmse']:.2f} | **{m['r2']:.3f}** |\n")

                f.write("\n**Top 5 Driving Features:**\n")
                for feat, imp in list(sc["feature_importance"].items())[:5]:
                    f.write(f"- `{feat}`: {imp}\n")
                f.write("\n---\n\n")

            f.write("## 2. Responsible AI & Advisory Safeguards\n\n")
            f.write("1. **Advisory Decision Support**: Predictions represent statistical estimations of vulnerability designed to proactively trigger academic tutoring and advisor mentoring.\n")
            f.write("2. **Non-Punitive Rule**: Predictions must never be used to make automated or exclusionary administrative decisions.\n")
            f.write("3. **Scientific Integrity**: Separating Scenario A (Intake) from Scenario C (Late-Stage) prevents misleading claims of early foresight based on late-term exam marks.\n")


if __name__ == "__main__":
    from src.ingestion.dataset_loader import DatasetLoader
    from src.preprocessing.transformer import EducationalTransformer

    loader = DatasetLoader()
    df_mat, df_por, _ = loader.load_raw_datasets()
    transformer = EducationalTransformer()
    students, courses, records = transformer.transform(df_mat, df_por)

    trainer = ModelTrainer()
    full_df = trainer.prepare_dataset(records, students)
    meta = trainer.train_and_evaluate_all_scenarios(full_df)

    print("=== Multi-Scenario Training & Benchmarking Completed Successfully ===")
    for k, sc in meta["scenarios"].items():
        print(f"[{k.upper()}] Best Classifier: {sc['best_classifier']} (ROC-AUC: {sc['classification'][sc['best_classifier']]['roc_auc']}) | Best Regressor: {sc['best_regressor']} (R2: {sc['regression'][sc['best_regressor']]['r2']})")
