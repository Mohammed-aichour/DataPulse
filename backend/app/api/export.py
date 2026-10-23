"""
Export & Power BI Integration Endpoints
Provides CSV streaming of raw/cleaned entities and analytical views,
and Power BI star-schema and DAX calculation specifications.
"""

from io import StringIO
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
import pandas as pd
from sqlalchemy.orm import Session
from DataPulse.database.connection import get_db
from DataPulse.database.models import AcademicRecordModel, CourseModel, StudentModel

router = APIRouter(prefix="/export", tags=["Export & Power BI"])


@router.get("/csv/{dataset_name}")
def export_csv(dataset_name: str, db: Session = Depends(get_db)):
    """Exports structured database tables as CSV for Power BI, Excel, or analytical pipelines."""
    buf = StringIO()

    if dataset_name == "students":
        records = db.query(StudentModel).all()
        data = [
            {
                "student_id": s.student_id,
                "school": s.school,
                "sex": s.sex,
                "age": s.age,
                "address": s.address,
                "famsize": s.famsize,
                "pstatus": s.pstatus,
                "medu": s.medu,
                "fedu": s.fedu,
                "mjob": s.mjob,
                "fjob": s.fjob,
                "reason": s.reason,
                "guardian": s.guardian,
                "nursery": s.nursery,
                "internet": s.internet
            }
            for s in records
        ]
    elif dataset_name == "academic_records":
        records = db.query(AcademicRecordModel).all()
        data = [
            {
                "record_id": r.record_id,
                "student_id": r.student_id,
                "course_code": r.course_code,
                "traveltime": r.traveltime,
                "studytime": r.studytime,
                "failures": r.failures,
                "schoolsup": r.schoolsup,
                "famsup": r.famsup,
                "paid": r.paid,
                "activities": r.activities,
                "higher": r.higher,
                "romantic": r.romantic,
                "famrel": r.famrel,
                "freetime": r.freetime,
                "goout": r.goout,
                "dalc": r.dalc,
                "walc": r.walc,
                "health": r.health,
                "absences": r.absences,
                "g1": r.g1,
                "g2": r.g2,
                "g3": r.g3,
                "parent_edu_avg": r.parent_edu_avg,
                "alcohol_index": r.alcohol_index,
                "study_to_social_ratio": r.study_to_social_ratio,
                "grade_delta": r.grade_delta,
                "academic_risk": r.academic_risk,
                "passing_status": r.passing_status,
                "performance_tier": r.performance_tier
            }
            for r in records
        ]
    elif dataset_name == "courses":
        records = db.query(CourseModel).all()
        data = [
            {
                "course_id": c.id,
                "course_code": c.course_code,
                "course_name": c.course_name,
                "department": c.department,
                "credits": c.credits
            }
            for c in records
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid dataset name. Choose: students, academic_records, courses")

    df = pd.DataFrame(data)
    df.to_csv(buf, index=False)
    csv_content = buf.getvalue()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=datapulse_{dataset_name}.csv"}
    )


@router.get("/powerbi-spec")
def get_powerbi_spec():
    """Returns technical metadata, Star-Schema guidance, and DAX formulas for Power BI report developers."""
    return {
        "star_schema": {
            "fact_table": "Fact_AcademicRecords (grain: 1 row per student per course enrollment)",
            "dimension_tables": [
                "Dim_Student (student_id PK, school, sex, age, address, family attributes)",
                "Dim_Course (course_id PK, course_code, course_name, department, credits)",
                "Dim_Date (academic_year, term, evaluation_period)"
            ],
            "relationships": [
                "Fact_AcademicRecords.student_id -> Dim_Student.student_id (Many to One, Single direction)",
                "Fact_AcademicRecords.course_id -> Dim_Course.id (Many to One, Single direction)"
            ]
        },
        "recommended_dax_measures": [
            {
                "name": "Pass Rate %",
                "dax": "DIVIDE(CALCULATE(COUNT(Fact_AcademicRecords[record_id]), Fact_AcademicRecords[passing_status] = TRUE), COUNT(Fact_AcademicRecords[record_id]), 0) * 100",
                "description": "Institutional percentage of passing course grades (G3 >= 10)."
            },
            {
                "name": "Average Final Grade",
                "dax": "AVERAGE(Fact_AcademicRecords[g3])",
                "description": "Mean final grade on the 0-20 Portuguese secondary scale."
            },
            {
                "name": "High Risk Student Count",
                "dax": "CALCULATE(DISTINCTCOUNT(Fact_AcademicRecords[student_id]), Fact_AcademicRecords[academic_risk] = 1)",
                "description": "Total unique students enrolled in at least one at-risk course."
            },
            {
                "name": "Absence Risk Correlation Index",
                "dax": "CALCULATE(AVERAGE(Fact_AcademicRecords[g3]), Fact_AcademicRecords[absences] > 10)",
                "description": "Average final grade for students exhibiting chronic absenteeism (>10 days)."
            }
        ],
        "connection_guide": {
            "database_type": "PostgreSQL or SQLite (via ODBC or CSV Direct Import)",
            "server": "localhost:5432 (or Docker container datapulse_db)",
            "database": "datapulse_db",
            "import_mode": "Import (recommended for fast visual interactivity) or DirectQuery"
        }
    }
