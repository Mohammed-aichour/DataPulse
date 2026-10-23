# DataPulse — Relational Database Architecture

## 1. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    STUDENTS ||--o{ ACADEMIC_RECORDS : "enrolls in"
    COURSES ||--o{ ACADEMIC_RECORDS : "contains"
    PIPELINE_EXECUTIONS ||--o{ DATA_IMPORTS : "audits"

    STUDENTS {
        int id PK
        string student_id UK "STU-0001 to STU-0674"
        string school "GP or MS"
        string sex "F or M"
        int age "15-22"
        string address "U or R"
        string famsize "LE3 or GT3"
        string pstatus "T or A"
        int medu "0-4"
        int fedu "0-4"
        string mjob "Occupation"
        string fjob "Occupation"
        string reason "School choice reason"
        string guardian "mother, father, other"
        string nursery "yes or no"
        string internet "yes or no"
        datetime created_at
    }

    COURSES {
        int id PK
        string course_code UK "MAT or POR"
        string course_name "Mathematics or Portuguese"
        string department "STEM or Humanities"
        int credits "6"
        string semester
    }

    ACADEMIC_RECORDS {
        int id PK
        string record_id UK "REC-00001 to REC-01044"
        string student_id FK "References students.student_id"
        int course_id FK "References courses.id"
        string course_code "MAT or POR"
        int traveltime "1-4"
        int studytime "1-4"
        int failures "0-4"
        string schoolsup "yes or no"
        string famsup "yes or no"
        string paid "yes or no"
        string activities "yes or no"
        string higher "yes or no"
        string romantic "yes or no"
        int famrel "1-5"
        int freetime "1-5"
        int goout "1-5"
        int dalc "1-5"
        int walc "1-5"
        int health "1-5"
        int absences "0-93"
        int g1 "0-20"
        int g2 "0-20"
        int g3 "0-20 (Target)"
        float parent_edu_avg
        float alcohol_index
        float study_to_social_ratio
        int grade_delta
        int academic_risk "1 if G3 < 10 else 0"
        bool passing_status "True if G3 >= 10"
        string performance_tier
        datetime created_at
    }

    PIPELINE_EXECUTIONS {
        int id PK
        datetime run_timestamp
        int records_processed
        float duration_seconds
        string status "SUCCESS, FAILED"
        float quality_score
        text details_json
    }

    PREDICTION_LOGS {
        int id PK
        datetime timestamp
        string course
        text features_json
        float predicted_grade
        int predicted_risk
        float risk_probability
        string model_name
        string model_version
    }

    DATA_IMPORTS {
        int id PK
        string source_name
        string file_name
        int row_count
        string checksum "SHA-256"
        datetime imported_at
        bool is_synthetic
        string status
    }
```

---

## 2. Table Schemas & Indices

1. **`students`**: Represents unique student individuals (674 resolved entities). Indexed on `student_id`.
2. **`courses`**: Course registry (`MAT` and `POR`). Indexed on `course_code`.
3. **`academic_records`**: Autonomous course enrollment instances (1,044 records). Compound index on `(student_id, course_id)` and single index on `academic_risk`.
4. **`pipeline_executions`**: Audits ETL and ML training cycles. Indexed on `run_timestamp`.
5. **`prediction_logs`**: Logs all inferences made through the REST API for model drift auditing.
6. **`data_imports`**: Tracks ingested CSV files and cryptographic checksums.

---

## 3. Analytical SQL Views

- `v_student_overview`: Denormalized analytical view combining demographics, course info, and academic indicators.
- `v_course_performance`: Aggregated metrics comparing enrollment counts, pass rates, average grades, and absences across subjects.
- `v_risk_analysis`: Evaluates correlations between academic risk and past failures, study habits, and alcohol consumption.
- `v_absence_impact`: Binned analysis showing grade degradation across cumulative absenteeism tiers.
- `v_performance_distribution`: Distribution of students across the 4 institutional tiers (*Needs Support*, *Satisfactory*, *Good*, *Excellent*).
