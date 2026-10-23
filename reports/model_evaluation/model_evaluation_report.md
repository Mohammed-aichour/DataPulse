# DataPulse — Multi-Scenario Machine Learning Evaluation Report

- **Trained At**: `2026-10-23T20:17:19.250242+00:00`
- **Methodological Architecture**: `3-Horizon Multi-Scenario Anti-Leakage Framework`
- **Dataset Split**: 835 Training records / 208 Unseen Test records (80/20 Stratified)

## 1. Multi-Horizon Predictive Benchmarks (Anti-Target Leakage)

To guarantee rigorous academic and production standards, models are evaluated across 3 distinct time horizons:

### Scenario A — Early Intake Risk Warning
*Pre-term orientation prediction using only demographic, family, lifestyle, and past academic history. Zero grade information used.*

**Classification Comparison (Target: Academic Risk G3 < 10):**

| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 5-Fold CV ROC-AUC |
|---|---|---|---|---|---|---|
| Logistic Regression | 81.3% | 64.0% | 34.8% | 0.451 | **0.774** | 76.3% (±3.2%) |
| Random Forest Classifier | 81.3% | 70.6% | 26.1% | 0.381 | **0.818** | 79.9% (±3.3%) |
| Gradient Boosting Classifier | 79.4% | 54.8% | 37.0% | 0.442 | **0.800** | 77.8% (±2.8%) |

**Regression Comparison (Target: Final Grade G3 [0-20]):**

| Model Name | MAE (Grade pts) | RMSE | R² Score |
|---|---|---|---|
| Ridge Regression | 2.38 pts | 3.34 | **0.274** |
| Random Forest Regressor | 2.37 pts | 3.24 | **0.317** |
| Gradient Boosting Regressor | 2.38 pts | 3.21 | **0.329** |

**Top 5 Driving Features:**
- `failures`: 0.1492
- `absences`: 0.0648
- `study_to_social_ratio`: 0.0495
- `course_code_MAT`: 0.0347
- `alcohol_index`: 0.0344

---

### Scenario B — Mid-Term Evaluation
*Mid-semester prediction after Period 1 exam results (G1) are published.*

**Classification Comparison (Target: Academic Risk G3 < 10):**

| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 5-Fold CV ROC-AUC |
|---|---|---|---|---|---|---|
| Logistic Regression | 85.7% | 68.2% | 65.2% | 0.667 | **0.931** | 93.0% (±1.4%) |
| Random Forest Classifier | 85.2% | 77.8% | 45.6% | 0.575 | **0.908** | 91.8% (±2.3%) |
| Gradient Boosting Classifier | 85.7% | 65.4% | 73.9% | 0.694 | **0.927** | 93.4% (±1.8%) |

**Regression Comparison (Target: Final Grade G3 [0-20]):**

| Model Name | MAE (Grade pts) | RMSE | R² Score |
|---|---|---|---|
| Ridge Regression | 1.56 pts | 2.19 | **0.690** |
| Random Forest Regressor | 1.41 pts | 1.98 | **0.746** |
| Gradient Boosting Regressor | 1.34 pts | 1.90 | **0.765** |

**Top 5 Driving Features:**
- `G1`: 3.1891
- `Fjob_health`: 0.6633
- `course_code_POR`: 0.6212
- `course_code_MAT`: 0.618
- `Fjob_other`: 0.3962

---

### Scenario C — Late-Stage Forecasting
*End-of-term final projection after Period 1 and Period 2 exams (G1 & G2) and grade trajectory are published.*

**Classification Comparison (Target: Academic Risk G3 < 10):**

| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 5-Fold CV ROC-AUC |
|---|---|---|---|---|---|---|
| Logistic Regression | 90.0% | 76.6% | 78.3% | 0.774 | **0.971** | 96.5% (±1.3%) |
| Random Forest Classifier | 90.4% | 78.3% | 78.3% | 0.783 | **0.971** | 96.7% (±1.1%) |
| Gradient Boosting Classifier | 90.0% | 76.6% | 78.3% | 0.774 | **0.968** | 96.2% (±1.2%) |

**Regression Comparison (Target: Final Grade G3 [0-20]):**

| Model Name | MAE (Grade pts) | RMSE | R² Score |
|---|---|---|---|
| Ridge Regression | 0.83 pts | 1.20 | **0.907** |
| Random Forest Regressor | 0.75 pts | 1.02 | **0.932** |
| Gradient Boosting Regressor | 0.76 pts | 1.08 | **0.924** |

**Top 5 Driving Features:**
- `G2`: 3.0968
- `G1`: 2.9003
- `grade_delta`: 0.8191
- `Fjob_health`: 0.6546
- `Fjob_at_home`: 0.5229

---

## 2. Responsible AI & Advisory Safeguards

1. **Advisory Decision Support**: Predictions represent statistical estimations of vulnerability designed to proactively trigger academic tutoring and advisor mentoring.
2. **Non-Punitive Rule**: Predictions must never be used to make automated or exclusionary administrative decisions.
3. **Scientific Integrity**: Separating Scenario A (Intake) from Scenario C (Late-Stage) prevents misleading claims of early foresight based on late-term exam marks.
