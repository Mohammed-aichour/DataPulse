"""
DataPulse Data Transformation & Feature Engineering Module
Resolves student entities across multi-course enrollments using robust 1-to-1 linkage,
computes educational indicators, and formats relational tables without intra-course duplicates.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class EducationalTransformer:
    # 13 attributes identified by Cortez & Silva (2008) for demographic student matching
    LINKAGE_ATTRIBUTES = [
        "school", "sex", "age", "address", "famsize", "Pstatus",
        "Medu", "Fedu", "Mjob", "Fjob", "reason", "nursery", "internet"
    ]

    def __init__(self, processed_data_dir: Optional[str] = None):
        if processed_data_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.processed_dir = base_dir / "data" / "processed"
        else:
            self.processed_dir = Path(processed_data_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def assign_performance_tier(g3: float) -> str:
        if g3 < 10:
            return "Needs Support"
        elif g3 < 14:
            return "Satisfactory"
        elif g3 < 16:
            return "Good"
        else:
            return "Excellent"

    def transform(self, df_mat: pd.DataFrame, df_por: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Transforms raw math and portuguese datasets into normalized relational entities:
        - students: unique student demographic entities
        - courses: course reference entities (MAT, POR)
        - academic_records: 1,044 student enrollments with grades, behavioural attributes and derived features
        
        Solves the demographic collision problem: uses occurrence ranking within demographic profiles
        to ensure no student is assigned multiple enrollments in the same course.
        """
        df_m = df_mat.copy()
        df_p = df_por.copy()

        df_m["course_code"] = "MAT"
        df_p["course_code"] = "POR"

        # Track occurrence index within demographic profile for both datasets
        # This prevents identical demographic profiles within the same course from colliding
        df_m["_occ"] = df_m.groupby(self.LINKAGE_ATTRIBUTES).cumcount()
        df_p["_occ"] = df_p.groupby(self.LINKAGE_ATTRIBUTES).cumcount()

        # Build courses reference
        courses_data = [
            {
                "course_id": 1,
                "course_code": "MAT",
                "course_name": "Mathematics",
                "department": "Department of Science and Mathematics",
                "credits": 6,
                "semester": "Full Academic Year"
            },
            {
                "course_id": 2,
                "course_code": "POR",
                "course_name": "Portuguese Language",
                "department": "Department of Humanities and Languages",
                "credits": 6,
                "semester": "Full Academic Year"
            }
        ]
        courses_df = pd.DataFrame(courses_data)

        # 1. Identify 1-to-1 matches between Math and Portuguese
        # Match keys: link_cols + _occ
        match_keys = self.LINKAGE_ATTRIBUTES + ["_occ"]
        cross_matched = pd.merge(
            df_m[match_keys],
            df_p[match_keys],
            on=match_keys,
            how="inner"
        )

        student_records = []
        student_id_counter = 1

        # Map cross-matched profiles
        cross_matched_map: Dict[Tuple, str] = {}
        for _, row in cross_matched.iterrows():
            key = tuple(row[col] for col in match_keys)
            sid = f"STU-{student_id_counter:04d}"
            student_id_counter += 1
            cross_matched_map[key] = sid

        # Assign student IDs to Math records
        m_sids = []
        m_linkage_status = []
        for _, row in df_m.iterrows():
            key = tuple(row[col] for col in match_keys)
            if key in cross_matched_map:
                m_sids.append(cross_matched_map[key])
                m_linkage_status.append("CROSS_COURSE_DUAL")
            else:
                sid = f"STU-{student_id_counter:04d}"
                student_id_counter += 1
                m_sids.append(sid)
                m_linkage_status.append("SINGLE_COURSE_MAT")

        df_m["student_id"] = m_sids
        df_m["linkage_status"] = m_linkage_status

        # Assign student IDs to Portuguese records
        p_sids = []
        p_linkage_status = []
        for _, row in df_p.iterrows():
            key = tuple(row[col] for col in match_keys)
            if key in cross_matched_map:
                p_sids.append(cross_matched_map[key])
                p_linkage_status.append("CROSS_COURSE_DUAL")
            else:
                sid = f"STU-{student_id_counter:04d}"
                student_id_counter += 1
                p_sids.append(sid)
                p_linkage_status.append("SINGLE_COURSE_POR")

        df_p["student_id"] = p_sids
        df_p["linkage_status"] = p_linkage_status

        # Combine verified enrollments
        combined = pd.concat([df_m, df_p], ignore_index=True)

        # Build canonical Student demographic entities
        student_cols = [
            "student_id", "school", "sex", "age", "address", "famsize",
            "Pstatus", "Medu", "Fedu", "Mjob", "Fjob", "reason",
            "guardian", "nursery", "internet"
        ]
        students_df = combined.drop_duplicates(subset=["student_id"])[student_cols].copy()
        students_df = students_df.sort_values(by="student_id").reset_index(drop=True)

        # Build AcademicRecord entities
        combined = pd.merge(
            combined,
            courses_df[["course_code", "course_id"]],
            on="course_code",
            how="left"
        )

        # Feature Engineering
        combined["parent_edu_avg"] = (combined["Medu"] + combined["Fedu"]) / 2.0
        combined["alcohol_index"] = (combined["Dalc"] * 5.0 + combined["Walc"] * 2.0) / 7.0
        combined["study_to_social_ratio"] = combined["studytime"] / (
            combined["goout"] + combined["freetime"] + 0.1
        )
        combined["grade_delta"] = combined["G2"] - combined["G1"]
        combined["academic_risk"] = (combined["G3"] < 10).astype(int)
        combined["passing_status"] = combined["G3"] >= 10
        combined["performance_tier"] = combined["G3"].apply(self.assign_performance_tier)
        combined["record_id"] = [f"REC-{i+1:05d}" for i in range(len(combined))]

        record_cols = [
            "record_id", "student_id", "course_id", "course_code",
            "traveltime", "studytime", "failures", "schoolsup", "famsup",
            "paid", "activities", "higher", "romantic", "famrel",
            "freetime", "goout", "Dalc", "Walc", "health", "absences",
            "G1", "G2", "G3", "parent_edu_avg", "alcohol_index",
            "study_to_social_ratio", "grade_delta", "academic_risk",
            "passing_status", "performance_tier", "linkage_status"
        ]
        records_df = combined[record_cols].copy()

        # Persist processed datasets
        students_df.to_csv(self.processed_dir / "students.csv", index=False)
        courses_df.to_csv(self.processed_dir / "courses.csv", index=False)
        records_df.to_csv(self.processed_dir / "academic_records.csv", index=False)

        return students_df, courses_df, records_df


if __name__ == "__main__":
    from src.ingestion.dataset_loader import DatasetLoader

    loader = DatasetLoader()
    df_mat, df_por, _ = loader.load_raw_datasets()
    transformer = EducationalTransformer()
    students, courses, records = transformer.transform(df_mat, df_por)

    print("=== Educational Transformation Audit Complete ===")
    print(f"- Total Ingestion Enrollments: {len(records)} records (395 MAT, 649 POR)")
    print(f"- Resolved Unique Students: {len(students)} unique physical individuals")
    print(f"- 1-to-1 Cross-Course Enrolled: {(records.duplicated(subset=['student_id'])).sum()} students")
    
    # Crucial check: verify that NO student is enrolled twice in the same course
    intra_dups = records.duplicated(subset=["student_id", "course_code"]).sum()
    print(f"- Intra-course student duplicates: {intra_dups} (must be exactly 0)")
    assert intra_dups == 0, "Error: Found duplicate enrollments of the same student in a single course!"
    print("Verification: Zero intra-course collisions confirmed.")
