"""
Data Analysis Agent
===================
Purpose: Load CSV data, handle missing values, and provide dataset summary.
"""

import os
import logging
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DataAnalysisAgent:
    """
    Agent responsible for data loading, preprocessing, and analysis.
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the Data Analysis Agent.
        """

        if data_path:
            self.data_path = data_path
        else:
            self.data_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "AI_Student_Success_Dropout_Dataset.csv",
            )

        self.df: Optional[pd.DataFrame] = None
        self.original_shape: Optional[Tuple[int, int]] = None

        logger.info(
            f"DataAnalysisAgent initialized with data path: {self.data_path}"
        )

    def load_data(self) -> pd.DataFrame:
        """Load dataset."""

        try:
            self.df = pd.read_csv(self.data_path)
            self.original_shape = self.df.shape

            logger.info(
                f"Data loaded successfully. Shape: {self.original_shape}"
            )

            return self.df

        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def handle_missing_values(self, strategy: str = "drop") -> pd.DataFrame:
        """Handle missing values."""

        if self.df is None:
            logger.warning("Data not loaded. Loading now...")
            self.df = self.load_data()

        assert self.df is not None

        initial_missing = self.df.isnull().sum().sum()
        logger.info(f"Initial missing values: {initial_missing}")

        if initial_missing == 0:
            logger.info("No missing values found")
            return self.df

        if strategy == "drop":
            self.df = self.df.dropna()

        elif strategy == "mean":
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns

            self.df[numeric_cols] = self.df[numeric_cols].fillna(
                self.df[numeric_cols].mean()
            )

        elif strategy == "median":
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns

            self.df[numeric_cols] = self.df[numeric_cols].fillna(
                self.df[numeric_cols].median()
            )

        elif strategy == "forward_fill":
            self.df = self.df.ffill()

        else:
            raise ValueError(
                "Strategy must be one of: "
                "'drop', 'mean', 'median', 'forward_fill'"
            )

        final_missing = self.df.isnull().sum().sum()

        logger.info(f"Final missing values: {final_missing}")

        return self.df

    def get_dataset_summary(self) -> Dict:
        """Return dataset summary."""

        if self.df is None:
            logger.warning("Data not loaded. Loading now...")
            self.df = self.load_data()

        assert self.df is not None

        summary = {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "data_types": self.df.dtypes.to_dict(),
            "missing_values": self.df.isnull().sum().to_dict(),
            "numeric_stats": self.df.describe().to_dict(),
            "categorical_stats": {},
        }

        categorical_cols = self.df.select_dtypes(
            include=["object"]
        ).columns

        for col in categorical_cols:
            summary["categorical_stats"][col] = (
                self.df[col].value_counts().to_dict()
            )

        return summary

    def get_descriptive_statistics(self) -> pd.DataFrame:
        """Return descriptive statistics."""

        if self.df is None:
            self.df = self.load_data()

        assert self.df is not None

        return self.df.describe()

    def detect_outliers(self, method: str = "iqr") -> Dict[str, list]:
        """Detect outliers."""

        if self.df is None:
            self.df = self.load_data()

        assert self.df is not None

        outliers: Dict[str, list] = {}

        numeric_cols = self.df.select_dtypes(
            include=[np.number]
        ).columns

        if method == "iqr":

            for col in numeric_cols:

                q1 = self.df[col].quantile(0.25)
                q3 = self.df[col].quantile(0.75)

                iqr = q3 - q1

                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr

                rows = self.df[
                    (self.df[col] < lower)
                    | (self.df[col] > upper)
                ]

                if not rows.empty:
                    outliers[col] = rows.index.tolist()

        elif method == "zscore":

            for col in numeric_cols:

                z = np.abs(
                    (self.df[col] - self.df[col].mean())
                    / self.df[col].std()
                )

                rows = self.df[z > 3]

                if not rows.empty:
                    outliers[col] = rows.index.tolist()

        return outliers


if __name__ == "__main__":

    agent = DataAnalysisAgent()

    df = agent.load_data()

    print("\nDataset loaded successfully!")
    print(df.shape)

    agent.handle_missing_values("drop")

    summary = agent.get_dataset_summary()

    print(summary["shape"])

    print(agent.get_descriptive_statistics())

    print(agent.detect_outliers())