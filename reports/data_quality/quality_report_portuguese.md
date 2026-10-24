# Institutional Data Quality Audit: Portuguese

- **Audit Generated At**: `2026-10-24T00:30:36.615640+00:00`
- **Overall Status**: **PASSED**
- **Institutional Quality Score**: **91.1 / 100**
- **Total Course Records**: 649
- **Total Schema Variables**: 33

## 1. Multi-Dimensional Quality Pillars

| Pillar | Weight | Score | Evaluation Method |
|---|---|---|---|
| **Completeness** | 25% | 100.0% | Null cell auditing across full matrix |
| **Schema Conformance** | 25% | 100.0% | Pydantic v2 type and domain validation |
| **Key Integrity** | 20% | 75.0% | Evaluates natural surrogate key availability |
| **Outlier Regularity** | 15% | 93.9% | IQR bounds auditing on grades and absences |
| **Granularity** | 15% | 80.0% | Evaluates metric temporal resolution |

## 2. Methodology & Limitation Notes

- Completeness: 100% (Zero missing cells detected in raw ingestion).
- Schema Validity: 100% (All 33 categorical and numeric bounds adhere to Pydantic v2 domain specifications).
- Key Integrity: 75% (Raw dataset lacks verified student surrogate keys; cross-course linkage is heuristic).
- Outlier Regularity: 93.9% (Penalized for 21 extreme absence records up to 93 days and 15 dropout zero-scores).
- Granularity: 80% (School absences are provided as cumulative term integer counts rather than daily swipe check-in records).

## 3. Target Variable (G3 Final Grade) Summary

- Mean: 11.91 / 20
- Standard Deviation: 3.23
- Range: [0, 19]
- Pass Rate (Score >= 10): 84.6%
- Dropout / Zero Scores: 15 records
