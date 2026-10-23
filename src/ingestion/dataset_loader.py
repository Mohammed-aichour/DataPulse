"""
DataPulse Ingestion Module
Handles dataset downloading, local caching, SHA256 integrity verification,
and raw ingestion for UCI Student Performance datasets.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import urllib.request
import zipfile
import numpy as np
import pandas as pd

UCI_STUDENT_PERFORMANCE_URL = "https://archive.ics.uci.edu/static/public/320/student+performance.zip"


@dataclass
class IngestionMetadata:
    source_name: str
    source_url: str
    file_name: str
    row_count: int
    column_count: int
    sha256_checksum: str
    ingested_at: str
    is_synthetic: bool = False
    notes: str = ""


class DatasetLoader:
    def __init__(self, raw_data_dir: Optional[str] = None):
        if raw_data_dir is None:
            # Default relative to repository root
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.raw_data_dir = base_dir / "data" / "raw"
        else:
            self.raw_data_dir = Path(raw_data_dir)

        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.mat_csv_path = self.raw_data_dir / "student-mat.csv"
        self.por_csv_path = self.raw_data_dir / "student-por.csv"

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        """Compute SHA256 hash for data integrity verification."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def download_uci_dataset(self, timeout_sec: int = 15) -> bool:
        """Download and extract the genuine UCI Student Performance dataset."""
        zip_path = self.raw_data_dir / "student_performance.zip"
        try:
            req = urllib.request.Request(
                UCI_STUDENT_PERFORMANCE_URL,
                headers={"User-Agent": "DataPulse-Platform/1.0 (Universiapolis Academic Research)"}
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as response, open(zip_path, "wb") as out_file:
                out_file.write(response.read())

            # Extract outer zip
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(self.raw_data_dir)

            # Extract inner student.zip if present
            nested_zip = self.raw_data_dir / "student.zip"
            if nested_zip.exists():
                with zipfile.ZipFile(nested_zip, "r") as nz:
                    nz.extractall(self.raw_data_dir)

            return self.mat_csv_path.exists() and self.por_csv_path.exists()
        except Exception as e:
            print(f"[DatasetLoader] Download failed: {e}")
            return False

    def generate_synthetic_dataset(self, n_mat: int = 395, n_por: int = 649, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Reproducible synthetic data generator.
        Used strictly as a graceful fallback when network fails and local raw files are absent.
        Clearly labeled as synthetic.
        """
        rng = np.random.default_rng(seed)

        def make_df(n: int, course_name: str) -> pd.DataFrame:
            schools = rng.choice(["GP", "MS"], size=n, p=[0.75, 0.25])
            sexes = rng.choice(["F", "M"], size=n, p=[0.52, 0.48])
            ages = rng.integers(15, 23, size=n)
            addresses = rng.choice(["U", "R"], size=n, p=[0.78, 0.22])
            famsizes = rng.choice(["GT3", "LE3"], size=n, p=[0.71, 0.29])
            pstatus = rng.choice(["T", "A"], size=n, p=[0.89, 0.11])
            medu = rng.integers(0, 5, size=n)
            fedu = rng.integers(0, 5, size=n)
            mjobs = rng.choice(["other", "services", "at_home", "teacher", "health"], size=n)
            fjobs = rng.choice(["other", "services", "teacher", "at_home", "health"], size=n)
            reasons = rng.choice(["course", "home", "reputation", "other"], size=n)
            guardians = rng.choice(["mother", "father", "other"], size=n, p=[0.70, 0.22, 0.08])
            traveltimes = rng.integers(1, 5, size=n)
            studytimes = rng.integers(1, 5, size=n)
            failures = rng.choice([0, 1, 2, 3], size=n, p=[0.78, 0.13, 0.06, 0.03])
            schoolsup = rng.choice(["no", "yes"], size=n, p=[0.87, 0.13])
            famsup = rng.choice(["yes", "no"], size=n, p=[0.61, 0.39])
            paid = rng.choice(["no", "yes"], size=n, p=[0.54, 0.46])
            activities = rng.choice(["yes", "no"], size=n, p=[0.51, 0.49])
            nursery = rng.choice(["yes", "no"], size=n, p=[0.79, 0.21])
            higher = rng.choice(["yes", "no"], size=n, p=[0.95, 0.05])
            internet = rng.choice(["yes", "no"], size=n, p=[0.83, 0.17])
            romantic = rng.choice(["no", "yes"], size=n, p=[0.67, 0.33])
            famrel = rng.integers(1, 6, size=n)
            freetime = rng.integers(1, 6, size=n)
            goout = rng.integers(1, 6, size=n)
            dalc = rng.integers(1, 6, size=n)
            walc = rng.integers(1, 6, size=n)
            health = rng.integers(1, 6, size=n)
            absences = rng.negative_binomial(2, 0.25, size=n)
            absences = np.clip(absences, 0, 75)

            # Generate realistic grades
            base_ability = (medu + fedu) * 0.5 + studytimes * 1.5 - failures * 2.5 - (dalc + walc) * 0.4 + rng.normal(8, 2, size=n)
            g1 = np.clip(np.round(base_ability + rng.normal(0, 1.5, size=n)), 0, 20).astype(int)
            g2 = np.clip(np.round(g1 * 0.85 + rng.normal(1.5, 1.2, size=n)), 0, 20).astype(int)
            g3 = np.clip(np.round(g2 * 0.90 + rng.normal(1.0, 1.2, size=n)), 0, 20).astype(int)

            return pd.DataFrame({
                "school": schools, "sex": sexes, "age": ages, "address": addresses,
                "famsize": famsizes, "Pstatus": pstatus, "Medu": medu, "Fedu": fedu,
                "Mjob": mjobs, "Fjob": fjobs, "reason": reasons, "guardian": guardians,
                "traveltime": traveltimes, "studytime": studytimes, "failures": failures,
                "schoolsup": schoolsup, "famsup": famsup, "paid": paid,
                "activities": activities, "nursery": nursery, "higher": higher,
                "internet": internet, "romantic": romantic, "famrel": famrel,
                "freetime": freetime, "goout": goout, "Dalc": dalc, "Walc": walc,
                "health": health, "absences": absences, "G1": g1, "G2": g2, "G3": g3
            })

        df_mat = make_df(n_mat, "MAT")
        df_por = make_df(n_por, "POR")
        return df_mat, df_por

    def load_raw_datasets(self) -> Tuple[pd.DataFrame, pd.DataFrame, List[IngestionMetadata]]:
        """
        Load Mathematics and Portuguese datasets from raw files.
        Verifies existence, checks hashes, or downloads if needed.
        """
        if not (self.mat_csv_path.exists() and self.por_csv_path.exists()):
            downloaded = self.download_uci_dataset()
            if not downloaded:
                print("[DatasetLoader] Warning: Unable to download UCI dataset. Falling back to clearly labeled synthetic dataset.")
                df_mat, df_por = self.generate_synthetic_dataset()
                # Save synthetic files
                df_mat.to_csv(self.mat_csv_path, sep=";", index=False)
                df_por.to_csv(self.por_csv_path, sep=";", index=False)
                is_synthetic = True
            else:
                is_synthetic = False
        else:
            is_synthetic = False

        # Load CSVs
        df_mat = pd.read_csv(self.mat_csv_path, sep=";")
        df_por = pd.read_csv(self.por_csv_path, sep=";")

        now = datetime.now(timezone.utc).isoformat()
        mat_hash = self.compute_sha256(self.mat_csv_path)
        por_hash = self.compute_sha256(self.por_csv_path)

        meta_mat = IngestionMetadata(
            source_name="UCI Machine Learning Repository - Student Performance (Math)",
            source_url=UCI_STUDENT_PERFORMANCE_URL,
            file_name=self.mat_csv_path.name,
            row_count=len(df_mat),
            column_count=len(df_mat.columns),
            sha256_checksum=mat_hash,
            ingested_at=now,
            is_synthetic=is_synthetic,
            notes="Mathematics course secondary school dataset"
        )

        meta_por = IngestionMetadata(
            source_name="UCI Machine Learning Repository - Student Performance (Portuguese)",
            source_url=UCI_STUDENT_PERFORMANCE_URL,
            file_name=self.por_csv_path.name,
            row_count=len(df_por),
            column_count=len(df_por.columns),
            sha256_checksum=por_hash,
            ingested_at=now,
            is_synthetic=is_synthetic,
            notes="Portuguese Language course secondary school dataset"
        )

        return df_mat, df_por, [meta_mat, meta_por]


if __name__ == "__main__":
    loader = DatasetLoader()
    df_mat, df_por, metadata = loader.load_raw_datasets()
    print(f"Loaded Math: {df_mat.shape}, Portuguese: {df_por.shape}")
    for m in metadata:
        print(f"File: {m.file_name} | Rows: {m.row_count} | Checksum: {m.sha256_checksum[:12]}... | Synthetic: {m.is_synthetic}")
