"""
DataPulse Database Loader Module
Loads transformed student profiles, courses, and academic records into the database.
Executes analytical SQL views, enforces atomic transactions, and logs pipeline executions.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from DataPulse.database.connection import SessionLocal, engine, init_db
from DataPulse.database.models import (
    AcademicRecordModel, CourseModel, DataImportModel,
    PipelineExecutionModel, StudentModel
)


class DatabaseLoader:
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session if db_session else SessionLocal()

    def setup_database_schema(self):
        """Initializes tables and compiles SQL analytical views."""
        init_db()

        # Load views from SQL file
        sql_views_path = Path(__file__).resolve().parent.parent.parent / "database" / "sql" / "views.sql"
        if sql_views_path.exists():
            with open(sql_views_path, "r", encoding="utf-8") as f:
                sql_content = f.read()

            with engine.connect() as conn:
                for statement in sql_content.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        try:
                            conn.execute(text(stmt))
                            conn.commit()
                        except Exception as e:
                            # Informational notice (e.g. view already exists)
                            pass

    def load_courses(self, courses_df: pd.DataFrame):
        try:
            for _, row in courses_df.iterrows():
                existing = self.db.query(CourseModel).filter_by(course_code=row["course_code"]).first()
                if not existing:
                    course = CourseModel(
                        id=int(row["course_id"]),
                        course_code=str(row["course_code"]),
                        course_name=str(row["course_name"]),
                        department=str(row["department"]),
                        credits=int(row["credits"]),
                        semester=str(row["semester"])
                    )
                    self.db.add(course)
                else:
                    existing.course_name = str(row["course_name"])
                    existing.department = str(row["department"])
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to load courses: {e}")

    def load_students(self, students_df: pd.DataFrame):
        """Idempotent loading of unique student demographic entities."""
        try:
            existing_map = {s.student_id: s for s in self.db.query(StudentModel).all()}
            new_students = []

            for _, row in students_df.iterrows():
                sid = str(row["student_id"])
                if sid in existing_map:
                    # Update existing record
                    curr = existing_map[sid]
                    curr.school = str(row["school"])
                    curr.sex = str(row["sex"])
                    curr.age = int(row["age"])
                    curr.address = str(row["address"])
                    curr.famsize = str(row["famsize"])
                    curr.pstatus = str(row["Pstatus"])
                    curr.medu = int(row["Medu"])
                    curr.fedu = int(row["Fedu"])
                    curr.mjob = str(row["Mjob"])
                    curr.fjob = str(row["Fjob"])
                    curr.reason = str(row["reason"])
                    curr.guardian = str(row["guardian"])
                    curr.nursery = str(row["nursery"])
                    curr.internet = str(row["internet"])
                else:
                    new_students.append(
                        StudentModel(
                            student_id=sid,
                            school=str(row["school"]),
                            sex=str(row["sex"]),
                            age=int(row["age"]),
                            address=str(row["address"]),
                            famsize=str(row["famsize"]),
                            pstatus=str(row["Pstatus"]),
                            medu=int(row["Medu"]),
                            fedu=int(row["Fedu"]),
                            mjob=str(row["Mjob"]),
                            fjob=str(row["Fjob"]),
                            reason=str(row["reason"]),
                            guardian=str(row["guardian"]),
                            nursery=str(row["nursery"]),
                            internet=str(row["internet"])
                        )
                    )

            if new_students:
                self.db.bulk_save_objects(new_students)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to load students: {e}")

    def load_academic_records(self, records_df: pd.DataFrame):
        """Idempotent loading of course enrollment records."""
        try:
            existing_map = {r.record_id: r for r in self.db.query(AcademicRecordModel).all()}
            new_records = []

            for _, row in records_df.iterrows():
                rid = str(row["record_id"])
                if rid in existing_map:
                    # Update metrics
                    curr = existing_map[rid]
                    curr.g1 = int(row["G1"])
                    curr.g2 = int(row["G2"])
                    curr.g3 = int(row["G3"])
                    curr.absences = int(row["absences"])
                    curr.studytime = int(row["studytime"])
                    curr.failures = int(row["failures"])
                    curr.academic_risk = int(row["academic_risk"])
                    curr.passing_status = bool(row["passing_status"])
                    curr.performance_tier = str(row["performance_tier"])
                else:
                    new_records.append(
                        AcademicRecordModel(
                            record_id=rid,
                            student_id=str(row["student_id"]),
                            course_id=int(row["course_id"]),
                            course_code=str(row["course_code"]),
                            traveltime=int(row["traveltime"]),
                            studytime=int(row["studytime"]),
                            failures=int(row["failures"]),
                            schoolsup=str(row["schoolsup"]),
                            famsup=str(row["famsup"]),
                            paid=str(row["paid"]),
                            activities=str(row["activities"]),
                            higher=str(row["higher"]),
                            romantic=str(row["romantic"]),
                            famrel=int(row["famrel"]),
                            freetime=int(row["freetime"]),
                            goout=int(row["goout"]),
                            dalc=int(row["Dalc"]),
                            walc=int(row["Walc"]),
                            health=int(row["health"]),
                            absences=int(row["absences"]),
                            g1=int(row["G1"]),
                            g2=int(row["G2"]),
                            g3=int(row["G3"]),
                            parent_edu_avg=float(row["parent_edu_avg"]),
                            alcohol_index=float(row["alcohol_index"]),
                            study_to_social_ratio=float(row["study_to_social_ratio"]),
                            grade_delta=int(row["grade_delta"]),
                            academic_risk=int(row["academic_risk"]),
                            passing_status=bool(row["passing_status"]),
                            performance_tier=str(row["performance_tier"])
                        )
                    )

            if new_records:
                self.db.bulk_save_objects(new_records)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to load academic records: {e}")

    def log_import(self, metadata_list: List[any]):
        try:
            for m in metadata_list:
                imp = DataImportModel(
                    source_name=m.source_name,
                    file_name=m.file_name,
                    row_count=m.row_count,
                    checksum=m.sha256_checksum,
                    is_synthetic=m.is_synthetic,
                    status="COMPLETED"
                )
                self.db.add(imp)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"[DatabaseLoader] Import log notice: {e}")

    def log_pipeline_execution(self, records_count: int, duration_sec: float, quality_score: float, details: dict):
        try:
            exec_log = PipelineExecutionModel(
                records_processed=records_count,
                duration_seconds=round(duration_sec, 2),
                status="SUCCESS",
                quality_score=quality_score,
                details_json=json.dumps(details)
            )
            self.db.add(exec_log)
            self.db.commit()
            return exec_log
        except Exception as e:
            self.db.rollback()
            print(f"[DatabaseLoader] Pipeline log notice: {e}")
            return None

    def close(self):
        self.db.close()
