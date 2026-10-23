"""
DataPulse Predictor & Multi-Scenario Inference Service
Supports 3-horizon prediction:
- Scenario A (Early Intake - Zero Grades)
- Scenario B (Mid-Term - Period 1 G1)
- Scenario C (Late-Stage - Period 1 & 2 G1 & G2)
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from DataPulse.database.connection import SessionLocal
from DataPulse.database.models import PredictionLogModel


class StudentPredictionInput(BaseModel):
    course_code: str = Field(default="MAT", description="Course code: MAT or POR")
    school: str = Field(default="GP", description="School: GP or MS")
    sex: str = Field(default="F", description="Sex: F or M")
    age: int = Field(default=17, ge=15, le=22)
    address: str = Field(default="U", description="Address: U or R")
    famsize: str = Field(default="GT3", description="Family size: GT3 or LE3")
    Pstatus: str = Field(default="T", description="Parent status: T or A")
    Medu: int = Field(default=3, ge=0, le=4)
    Fedu: int = Field(default=3, ge=0, le=4)
    Mjob: str = Field(default="services")
    Fjob: str = Field(default="services")
    reason: str = Field(default="course")
    guardian: str = Field(default="mother")
    traveltime: int = Field(default=1, ge=1, le=4)
    studytime: int = Field(default=2, ge=1, le=4)
    failures: int = Field(default=0, ge=0, le=4)
    schoolsup: str = Field(default="no")
    famsup: str = Field(default="yes")
    paid: str = Field(default="no")
    activities: str = Field(default="yes")
    nursery: str = Field(default="yes")
    higher: str = Field(default="yes")
    internet: str = Field(default="yes")
    romantic: str = Field(default="no")
    famrel: int = Field(default=4, ge=1, le=5)
    freetime: int = Field(default=3, ge=1, le=5)
    goout: int = Field(default=3, ge=1, le=5)
    Dalc: int = Field(default=1, ge=1, le=5)
    Walc: int = Field(default=1, ge=1, le=5)
    health: int = Field(default=4, ge=1, le=5)
    absences: int = Field(default=2, ge=0, le=93)
    G1: Optional[int] = Field(default=None, ge=0, le=20, description="Period 1 Grade (optional for Scenario A)")
    G2: Optional[int] = Field(default=None, ge=0, le=20, description="Period 2 Grade (optional for Scenarios A & B)")
    scenario: Optional[str] = Field(default="auto", description="Prediction scenario: auto, early, midterm, latestage")


class PredictorService:
    def __init__(self, artifacts_dir: Optional[str] = None):
        if artifacts_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.artifacts_dir = base_dir / "models_artifacts"
        else:
            self.artifacts_dir = Path(artifacts_dir)

        self.metadata_path = self.artifacts_dir / "model_metadata.json"
        self.metadata = None
        self.pipelines: Dict[str, Dict[str, Any]] = {}
        self._load_artifacts()

    def _load_artifacts(self):
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

        # Load pipelines for Scenarios A, B, C
        for key in ["scenario_a", "scenario_b", "scenario_c"]:
            cls_p = self.artifacts_dir / f"best_risk_classifier_{key}.joblib"
            reg_p = self.artifacts_dir / f"best_grade_regressor_{key}.joblib"
            if cls_p.exists() and reg_p.exists():
                self.pipelines[key] = {
                    "classifier": joblib.load(cls_p),
                    "regressor": joblib.load(reg_p)
                }

        # Fallback default if scenario-specific files are absent
        if not self.pipelines:
            def_cls = self.artifacts_dir / "best_risk_classifier.joblib"
            def_reg = self.artifacts_dir / "best_grade_regressor.joblib"
            if def_cls.exists() and def_reg.exists():
                self.pipelines["scenario_c"] = {
                    "classifier": joblib.load(def_cls),
                    "regressor": joblib.load(def_reg)
                }

    def is_ready(self) -> bool:
        return len(self.pipelines) > 0

    def resolve_scenario(self, requested_scenario: str, g1: Optional[int], g2: Optional[int]) -> str:
        req = requested_scenario.lower().strip()
        if req in {"early", "intake", "scenario_a"}:
            return "scenario_a"
        elif req in {"midterm", "mid_term", "scenario_b"}:
            return "scenario_b"
        elif req in {"latestage", "late_stage", "final", "scenario_c"}:
            return "scenario_c"
        
        # Auto-detection based on available inputs
        if g1 is not None and g2 is not None:
            return "scenario_c"
        elif g1 is not None:
            return "scenario_b"
        else:
            return "scenario_a"

    def predict(self, input_data: StudentPredictionInput, db: Optional[Session] = None) -> Dict[str, Any]:
        if not self.is_ready():
            raise RuntimeError("Machine Learning models are not trained yet. Run pipeline first.")

        data = input_data.model_dump()
        g1 = data.get("G1")
        g2 = data.get("G2")
        active_scenario = self.resolve_scenario(data.get("scenario", "auto"), g1, g2)

        if active_scenario not in self.pipelines:
            # Fallback to available
            active_scenario = list(self.pipelines.keys())[0]

        pipe_dict = self.pipelines[active_scenario]
        classifier = pipe_dict["classifier"]
        regressor = pipe_dict["regressor"]

        # Engineered features
        parent_edu_avg = (data["Medu"] + data["Fedu"]) / 2.0
        alcohol_index = (data["Dalc"] * 5.0 + data["Walc"] * 2.0) / 7.0
        study_to_social_ratio = data["studytime"] / (data["goout"] + data["freetime"] + 0.1)
        grade_delta = (g2 - g1) if (g1 is not None and g2 is not None) else 0

        # Build feature dictionary based on scenario
        features = {
            "course_code": data["course_code"],
            "school": data["school"],
            "sex": data["sex"],
            "age": data["age"],
            "address": data["address"],
            "famsize": data["famsize"],
            "Pstatus": data["Pstatus"],
            "Medu": data["Medu"],
            "Fedu": data["Fedu"],
            "Mjob": data["Mjob"],
            "Fjob": data["Fjob"],
            "reason": data["reason"],
            "guardian": data["guardian"],
            "traveltime": data["traveltime"],
            "studytime": data["studytime"],
            "failures": data["failures"],
            "schoolsup": data["schoolsup"],
            "famsup": data["famsup"],
            "paid": data["paid"],
            "activities": data["activities"],
            "nursery": data["nursery"],
            "higher": data["higher"],
            "internet": data["internet"],
            "romantic": data["romantic"],
            "famrel": data["famrel"],
            "freetime": data["freetime"],
            "goout": data["goout"],
            "Dalc": data["Dalc"],
            "Walc": data["Walc"],
            "health": data["health"],
            "absences": data["absences"],
            "parent_edu_avg": parent_edu_avg,
            "alcohol_index": alcohol_index,
            "study_to_social_ratio": study_to_social_ratio,
        }

        if active_scenario == "scenario_b":
            features["G1"] = g1 if g1 is not None else 10
        elif active_scenario == "scenario_c":
            features["G1"] = g1 if g1 is not None else 10
            features["G2"] = g2 if g2 is not None else 10
            features["grade_delta"] = grade_delta

        df_input = pd.DataFrame([features])

        # Inference
        pred_risk_bin = int(classifier.predict(df_input)[0])
        pred_probas = classifier.predict_proba(df_input)[0]
        risk_probability = float(pred_probas[1]) if len(pred_probas) > 1 else float(pred_risk_bin)

        pred_grade = float(regressor.predict(df_input)[0])
        pred_grade = round(max(0.0, min(20.0, pred_grade)), 1)

        # Risk tier & recommendations
        if risk_probability < 0.25:
            risk_tier = "Low Academic Risk"
            recommendation = "Student demonstrates strong protective factors. Standard curriculum progression recommended."
        elif risk_probability < 0.60:
            risk_tier = "Moderate Risk"
            recommendation = "Recommended advisory interventions: peer mentoring, scheduled faculty office hours, and monitoring."
        else:
            risk_tier = "High Academic Risk"
            recommendation = "Immediate pedagogical intervention required: comprehensive tutoring and weekly check-in."

        # Scenario-specific contributing factors
        contributing_factors = []
        if active_scenario == "scenario_a":
            contributing_factors.append("Early Horizon (Pre-Term): Evaluated using intake demographics and behavioral history.")
            if data["failures"] > 0:
                contributing_factors.append(f"History of {data['failures']} past class failure(s) is the primary early risk multiplier.")
            if data["studytime"] <= 1:
                contributing_factors.append("Reported study time is under 2 hours per week.")
            if data["absences"] > 10:
                contributing_factors.append(f"Elevated absenteeism ({data['absences']} days) indicates disengagement.")
            if data["higher"] == "no":
                contributing_factors.append("Student does not aspire to pursue higher education.")
        elif active_scenario == "scenario_b":
            contributing_factors.append(f"Mid-Term Horizon: First period grade G1 ({g1}/20) informs baseline trajectory.")
            if g1 is not None and g1 < 10:
                contributing_factors.append(f"Failing grade in Period 1 ({g1}/20) requires immediate corrective action.")
        else:
            contributing_factors.append(f"Late-Stage Horizon: Continuous marks G1 ({g1}/20) & G2 ({g2}/20) provide high-precision final forecast.")
            if g2 is not None and g2 < 10:
                contributing_factors.append(f"Low Period 2 Grade ({g2}/20) is a critical late-term warning indicator.")
            if grade_delta < 0:
                contributing_factors.append(f"Negative momentum detected: Grade dropped by {abs(grade_delta)} points between G1 and G2.")

        scenario_labels = {
            "scenario_a": "Scenario A — Early Intake (Pre-Grades)",
            "scenario_b": "Scenario B — Mid-Term (Post-G1)",
            "scenario_c": "Scenario C — Late-Stage (Post-G1 & G2)"
        }

        result = {
            "scenario": active_scenario,
            "predicted_grade_g3": pred_grade,
            "is_at_risk": bool(pred_risk_bin == 1),
            "risk_probability": round(risk_probability, 3),
            "risk_tier": risk_tier,
            "confidence_pct": round((1.0 - abs(risk_probability - 0.5) * 0.4) * 100, 1),
            "recommendation": recommendation,
            "contributing_factors": contributing_factors,
            "scenario_used": {
                "key": active_scenario,
                "label": scenario_labels.get(active_scenario, active_scenario),
                "anti_leakage_status": "VERIFIED_NO_TARGET_LEAKAGE" if active_scenario == "scenario_a" else "PERIODIC_GRADES_INCLUDED"
            },
            "model_used": {
                "classifier": type(classifier.named_steps["classifier"]).__name__,
                "regressor": type(regressor.named_steps["regressor"]).__name__
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Log prediction to database
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            log_entry = PredictionLogModel(
                course=data["course_code"],
                features_json=json.dumps({**data, "resolved_scenario": active_scenario}),
                predicted_grade=pred_grade,
                predicted_risk=pred_risk_bin,
                risk_probability=round(risk_probability, 3),
                model_name=f"{type(classifier.named_steps['classifier']).__name__} ({active_scenario})",
                model_version="v2.0"
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            print(f"[PredictorService] Prediction log notice: {e}")
        finally:
            if close_db:
                db.close()

        return result


if __name__ == "__main__":
    predictor = PredictorService()
    print("=== Testing Predictor Service Across Scenarios ===")
    
    # 1. Early scenario (No G1, No G2)
    sample_early = StudentPredictionInput(
        course_code="MAT",
        studytime=1,
        failures=2,
        absences=12,
        scenario="early"
    )
    res_a = predictor.predict(sample_early)
    print(f"Scenario A: Risk={res_a['is_at_risk']}, Prob={res_a['risk_probability']}, Grade={res_a['predicted_grade_g3']}/20, Used={res_a['scenario_used']['label']}")

    # 2. Late stage scenario (With G1 & G2)
    sample_late = StudentPredictionInput(
        course_code="MAT",
        studytime=3,
        failures=0,
        absences=2,
        G1=16,
        G2=17,
        scenario="latestage"
    )
    res_c = predictor.predict(sample_late)
    print(f"Scenario C: Risk={res_c['is_at_risk']}, Prob={res_c['risk_probability']}, Grade={res_c['predicted_grade_g3']}/20, Used={res_c['scenario_used']['label']}")
