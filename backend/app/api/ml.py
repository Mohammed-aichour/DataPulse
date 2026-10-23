"""
Machine Learning & Predictive Intelligence API Endpoints
Provides multi-scenario evaluation metrics and real-time inference.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DataPulse.backend.app.schemas.schemas import PredictionRequest, PredictionResponse
from DataPulse.database.connection import get_db
from DataPulse.src.ml.predictor import PredictorService, StudentPredictionInput

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/model-info")
def get_model_info():
    predictor = PredictorService()
    if not predictor.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Models not trained yet. Run the ETL pipeline first via POST /api/pipeline/run."
        )
    return predictor.metadata


@router.get("/evaluation")
def get_model_evaluation():
    predictor = PredictorService()
    if not predictor.is_ready() or not predictor.metadata:
        raise HTTPException(
            status_code=503,
            detail="Evaluation data unavailable. Run the ETL & ML pipeline."
        )

    meta = predictor.metadata
    return {
        "framework": meta.get("framework", "3-Horizon Multi-Scenario Anti-Leakage Framework"),
        "active_default_scenario": meta.get("active_default_scenario", "scenario_c"),
        "scenarios": meta.get("scenarios", {}),
        "best_classifier": meta.get("best_classifier"),
        "best_regressor": meta.get("best_regressor"),
        "classification_comparison": meta.get("classification_metrics", {}),
        "regression_comparison": meta.get("regression_metrics", {}),
        "top_features": meta.get("feature_importance", {}),
        "dataset_split": {
            "train_samples": meta.get("train_samples", 835),
            "test_samples": meta.get("test_samples", 209)
        },
        "trained_at": meta.get("trained_at"),
        "responsible_ai_notice": (
            "Predictions are statistical estimations for student support, not automated academic decisions. "
            "Interventions must be led by human educational advisors."
        )
    }


@router.post("/predict", response_model=PredictionResponse)
def predict_student_performance(request: PredictionRequest, db: Session = Depends(get_db)):
    predictor = PredictorService()
    if not predictor.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Machine learning models are not initialized. Run pipeline first."
        )

    try:
        input_data = StudentPredictionInput(**request.model_dump())
        result = predictor.predict(input_data, db=db)
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")
