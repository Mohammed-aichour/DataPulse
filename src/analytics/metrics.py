"""
DataPulse Analytics Engine
Computes real educational KPIs, demographic breakdowns,
grade distributions, and risk correlations from database records.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sqlalchemy import Integer, func, text
from sqlalchemy.orm import Session
from DataPulse.database.connection import SessionLocal
from DataPulse.database.models import AcademicRecordModel, CourseModel, DataImportModel, PipelineExecutionModel, StudentModel


class CampusAnalyticsEngine:
    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def get_db(self) -> Session:
        return self._db if self._db else SessionLocal()

    def get_overview_kpis(self) -> Dict[str, Any]:
        """Compute top-level executive KPIs directly from live database tables."""
        db = self.get_db()
        try:
            total_students = db.query(StudentModel).count()
            total_enrollments = db.query(AcademicRecordModel).count()

            if total_enrollments == 0:
                return {
                    "total_students": 0,
                    "total_enrollments": 0,
                    "avg_final_grade": 0.0,
                    "pass_rate_pct": 0.0,
                    "risk_count": 0,
                    "risk_rate_pct": 0.0,
                    "avg_absences": 0.0,
                    "data_quality_score": 100.0,
                    "courses_count": 0,
                    "last_pipeline_run": None,
                }

            avg_g3 = db.query(func.avg(AcademicRecordModel.g3)).scalar() or 0.0
            passing_count = db.query(AcademicRecordModel).filter(AcademicRecordModel.passing_status == True).count()
            risk_count = db.query(AcademicRecordModel).filter(AcademicRecordModel.academic_risk == 1).count()
            avg_absences = db.query(func.avg(AcademicRecordModel.absences)).scalar() or 0.0
            courses_count = db.query(CourseModel).count()

            # Latest pipeline execution
            latest_run = (
                db.query(PipelineExecutionModel)
                .order_by(PipelineExecutionModel.run_timestamp.desc())
                .first()
            )

            quality_score = latest_run.quality_score if latest_run else 100.0
            last_run_time = latest_run.run_timestamp.isoformat() if latest_run else None

            pass_rate = (passing_count / total_enrollments) * 100.0
            risk_rate = (risk_count / total_enrollments) * 100.0

            return {
                "total_students": total_students,
                "total_enrollments": total_enrollments,
                "avg_final_grade": round(float(avg_g3), 2),
                "pass_rate_pct": round(pass_rate, 1),
                "risk_count": risk_count,
                "risk_rate_pct": round(risk_rate, 1),
                "avg_absences": round(float(avg_absences), 1),
                "data_quality_score": quality_score,
                "courses_count": courses_count,
                "last_pipeline_run": last_run_time,
            }
        finally:
            if not self._db:
                db.close()

    def get_course_performance(self) -> List[Dict[str, Any]]:
        """Comparative metrics between Mathematics and Portuguese courses."""
        db = self.get_db()
        try:
            results = (
                db.query(
                    CourseModel.course_code,
                    CourseModel.course_name,
                    CourseModel.department,
                    func.count(AcademicRecordModel.id).label("enrollments"),
                    func.avg(AcademicRecordModel.g1).label("avg_g1"),
                    func.avg(AcademicRecordModel.g2).label("avg_g2"),
                    func.avg(AcademicRecordModel.g3).label("avg_g3"),
                    func.avg(AcademicRecordModel.absences).label("avg_absences"),
                    func.avg(AcademicRecordModel.studytime).label("avg_studytime"),
                    func.avg(AcademicRecordModel.failures).label("avg_failures"),
                    func.sum(func.cast(AcademicRecordModel.passing_status, Integer if db.bind.dialect.name == "sqlite" else Integer)).label("pass_count")
                )
                .join(AcademicRecordModel, CourseModel.id == AcademicRecordModel.course_id)
                .group_by(CourseModel.course_code, CourseModel.course_name, CourseModel.department)
                .all()
            )

            courses = []
            for r in results:
                enrollments = r.enrollments or 1
                pass_count = r.pass_count or 0
                courses.append({
                    "course_code": r.course_code,
                    "course_name": r.course_name,
                    "department": r.department,
                    "enrollments": enrollments,
                    "avg_g1": round(float(r.avg_g1 or 0), 2),
                    "avg_g2": round(float(r.avg_g2 or 0), 2),
                    "avg_g3": round(float(r.avg_g3 or 0), 2),
                    "avg_absences": round(float(r.avg_absences or 0), 1),
                    "avg_studytime": round(float(r.avg_studytime or 0), 2),
                    "avg_failures": round(float(r.avg_failures or 0), 2),
                    "pass_rate_pct": round(float(pass_count) / enrollments * 100.0, 1),
                })
            return courses
        finally:
            if not self._db:
                db.close()

    def get_grade_distribution(self) -> List[Dict[str, Any]]:
        """Binned grade distribution (0-20 scale) across periods G1, G2, G3."""
        db = self.get_db()
        try:
            records = db.query(AcademicRecordModel.g1, AcademicRecordModel.g2, AcademicRecordModel.g3).all()
            if not records:
                return []

            df = pd.DataFrame(records, columns=["g1", "g2", "g3"])
            bins = [0, 5, 8, 10, 12, 14, 16, 18, 21]
            labels = ["0-4", "5-7", "8-9", "10-11", "12-13", "14-15", "16-17", "18-20"]

            df["g1_bin"] = pd.cut(df["g1"], bins=bins, labels=labels, right=False)
            df["g2_bin"] = pd.cut(df["g2"], bins=bins, labels=labels, right=False)
            df["g3_bin"] = pd.cut(df["g3"], bins=bins, labels=labels, right=False)

            g1_counts = df["g1_bin"].value_counts().to_dict()
            g2_counts = df["g2_bin"].value_counts().to_dict()
            g3_counts = df["g3_bin"].value_counts().to_dict()

            distribution = []
            for label in labels:
                distribution.append({
                    "grade_range": label,
                    "period_1": int(g1_counts.get(label, 0)),
                    "period_2": int(g2_counts.get(label, 0)),
                    "final_g3": int(g3_counts.get(label, 0)),
                })
            return distribution
        finally:
            if not self._db:
                db.close()

    def get_performance_by_factor(self, factor_name: str) -> List[Dict[str, Any]]:
        """Calculates academic performance segmented by specific educational/lifestyle factors."""
        db = self.get_db()
        try:
            # Query joined dataframe
            query = (
                db.query(
                    StudentModel.sex,
                    StudentModel.school,
                    StudentModel.address,
                    StudentModel.internet,
                    AcademicRecordModel.higher,
                    AcademicRecordModel.studytime,
                    AcademicRecordModel.failures,
                    AcademicRecordModel.g3,
                    AcademicRecordModel.academic_risk,
                    AcademicRecordModel.passing_status,
                    AcademicRecordModel.alcohol_index,
                    AcademicRecordModel.parent_edu_avg,
                    AcademicRecordModel.absences,
                )
                .join(AcademicRecordModel, StudentModel.student_id == AcademicRecordModel.student_id)
            )
            df = pd.read_sql(query.statement, db.bind)
            if df.empty:
                return []

            if factor_name == "studytime":
                labels = {1: "< 2 hours", 2: "2 - 5 hours", 3: "5 - 10 hours", 4: "> 10 hours"}
                df["group"] = df["studytime"].map(labels)
            elif factor_name == "failures":
                labels = {0: "0 Failures", 1: "1 Failure", 2: "2 Failures", 3: "3+ Failures"}
                df["group"] = df["failures"].apply(lambda x: labels.get(x, "3+ Failures"))
            elif factor_name == "parent_edu":
                df["group"] = pd.cut(
                    df["parent_edu_avg"],
                    bins=[-0.1, 1.5, 2.5, 3.5, 4.1],
                    labels=["Primary / None", "Middle School", "Secondary", "Higher Education"]
                )
            elif factor_name == "school":
                df["group"] = df["school"].map({"GP": "Gabriel Pereira (GP)", "MS": "Mousinho da Silveira (MS)"})
            elif factor_name == "sex":
                df["group"] = df["sex"].map({"F": "Female", "M": "Male"})
            elif factor_name == "internet":
                df["group"] = df["internet"].map({"yes": "Internet Access", "no": "No Internet"})
            elif factor_name == "absences":
                df["group"] = pd.cut(
                    df["absences"],
                    bins=[-0.1, 0.5, 5.5, 10.5, 20.5, 100],
                    labels=["0 Days (Perfect)", "1-5 Days (Low)", "6-10 Days (Moderate)", "11-20 Days (Elevated)", "21+ Days (Severe)"]
                )
            else:
                return []

            grouped = df.groupby("group", observed=False).agg(
                student_count=("g3", "count"),
                avg_grade=("g3", "mean"),
                pass_rate=("passing_status", lambda x: (x == 1).mean() * 100.0),
                risk_rate=("academic_risk", lambda x: (x == 1).mean() * 100.0)
            ).reset_index()

            results = []
            for _, r in grouped.iterrows():
                results.append({
                    "factor_group": str(r["group"]),
                    "student_count": int(r["student_count"]),
                    "avg_grade": round(float(r["avg_grade"]), 2),
                    "pass_rate_pct": round(float(r["pass_rate"]), 1),
                    "risk_rate_pct": round(float(r["risk_rate"]), 1),
                })
            return results
        finally:
            if not self._db:
                db.close()

    def get_correlations(self) -> List[Dict[str, Any]]:
        """Correlation coefficients between student features and Final Grade (G3)."""
        db = self.get_db()
        try:
            records = db.query(
                AcademicRecordModel.g3,
                AcademicRecordModel.g1,
                AcademicRecordModel.g2,
                AcademicRecordModel.studytime,
                AcademicRecordModel.failures,
                AcademicRecordModel.absences,
                AcademicRecordModel.parent_edu_avg,
                AcademicRecordModel.alcohol_index,
                AcademicRecordModel.famrel,
                AcademicRecordModel.freetime,
                AcademicRecordModel.goout,
                AcademicRecordModel.health,
            ).all()

            if not records:
                return []

            df = pd.DataFrame(records)
            corr_series = df.corr()["g3"].drop("g3").sort_values(ascending=False)

            descriptions = {
                "g2": "Period 2 Grade",
                "g1": "Period 1 Grade",
                "parent_edu_avg": "Parental Education Capital",
                "studytime": "Weekly Study Time",
                "famrel": "Family Relationship Quality",
                "health": "Current Health Status",
                "freetime": "Free Time After School",
                "absences": "Total School Absences",
                "goout": "Going Out With Friends",
                "alcohol_index": "Weekly Alcohol Consumption",
                "failures": "Past Academic Failures",
            }

            correlations = []
            for col, val in corr_series.items():
                correlations.append({
                    "feature": col,
                    "label": descriptions.get(col, col),
                    "correlation": round(float(val), 3),
                    "impact": "Positive" if val > 0 else "Negative",
                    "magnitude": "Strong" if abs(val) >= 0.4 else ("Moderate" if abs(val) >= 0.15 else "Weak")
                })
            return correlations
        finally:
            if not self._db:
                db.close()

    def get_data_quality_summary(self) -> Dict[str, Any]:
        """Summary of data freshness, total imports, and quality history."""
        db = self.get_db()
        try:
            imports = db.query(DataImportModel).order_by(DataImportModel.imported_at.desc()).all()
            executions = db.query(PipelineExecutionModel).order_by(PipelineExecutionModel.run_timestamp.desc()).limit(10).all()

            return {
                "imports": [
                    {
                        "source_name": i.source_name,
                        "file_name": i.file_name,
                        "row_count": i.row_count,
                        "checksum": i.checksum,
                        "imported_at": i.imported_at.isoformat(),
                        "is_synthetic": i.is_synthetic,
                        "status": i.status
                    }
                    for i in imports
                ],
                "recent_executions": [
                    {
                        "id": e.id,
                        "run_timestamp": e.run_timestamp.isoformat(),
                        "records_processed": e.records_processed,
                        "duration_seconds": e.duration_seconds,
                        "status": e.status,
                        "quality_score": e.quality_score
                    }
                    for e in executions
                ]
            }
        finally:
            if not self._db:
                db.close()
