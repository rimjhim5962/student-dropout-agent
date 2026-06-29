"""
Data Analysis Agent
===================
Purpose: Load CSV data, handle missing values, and provide dataset summary.

Architecture:
- Loads CSV files from the data directory
- Performs exploratory data analysis (EDA)
- Handles missing values using various strategies
- Provides statistical summaries and insights
"""

import os

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataAnalysisAgent:
    """
    Agent responsible for data loading, preprocessing, and analysis.
    
    This agent:
    1. Loads CSV files
    2. Handles missing values
    3. Provides dataset statistics and summaries
    4. Detects data anomalies
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the Data Analysis Agent.
        
        Args:
            data_path (str): Path to the CSV file. If None, loads default dataset.
        """
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
    "data",
    "AI_Student_Success_Dropout_Dataset.csv"
      )
        self.df = None
        self.original_shape = None
        logger.info(f"DataAnalysisAgent initialized with data path: {self.data_path}")
    
    def load_data(self) -> pd.DataFrame:
        """
        Load CSV data from the specified path.
        
        Returns:
            pd.DataFrame: Loaded dataset
            
        Raises:
            FileNotFoundError: If the CSV file is not found
            pd.errors.ParserError: If the CSV file is corrupted
        """
        try:
            self.df = pd.read_csv(self.data_path)
            self.original_shape = self.df.shape
            logger.info(f"Data loaded successfully. Shape: {self.original_shape}")
            return self.df
        except FileNotFoundError:
            logger.error(f"File not found: {self.data_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def handle_missing_values(self, strategy: str = 'drop') -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            strategy (str): Strategy to handle missing values
                - 'drop': Drop rows with missing values
                - 'mean': Fill with mean values (numeric columns)
                - 'median': Fill with median values (numeric columns)
                - 'forward_fill': Forward fill missing values
                
        Returns:
            pd.DataFrame: Dataset with handled missing values
        """
        if self.df is None:
            logger.warning("Data not loaded. Loading now...")
            self.load_data()
        
        initial_missing = self.df.isnull().sum().sum()
        logger.info(f"Initial missing values: {initial_missing}")
        
        if initial_missing == 0:
            logger.info("No missing values found")
            return self.df
        
        if strategy == 'drop':
            self.df = self.df.dropna()
        elif strategy == 'mean':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
        elif strategy == 'median':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
        elif strategy == 'forward_fill':
            self.df = self.df.fillna(method='ffill')
        
        final_missing = self.df.isnull().sum().sum()
        logger.info(f"Final missing values: {final_missing}")
        
        return self.df
    
    def get_dataset_summary(self) -> Dict:
        """
        Generate a comprehensive summary of the dataset.
        
        Returns:
            Dict: Dictionary containing dataset statistics
        """
        if self.df is None:
            logger.warning("Data not loaded. Loading now...")
            self.load_data()
        
        summary = {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'data_types': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'numeric_stats': self.df.describe().to_dict(),
            'categorical_stats': {}
        }
        
        # Add categorical statistics
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            summary['categorical_stats'][col] = self.df[col].value_counts().to_dict()
        
        return summary
    
    def get_descriptive_statistics(self) -> pd.DataFrame:
        """
        Get descriptive statistics for numeric columns.
        
        Returns:
            pd.DataFrame: Descriptive statistics
        """
        if self.df is None:
            self.load_data()
        
        return self.df.describe()
    
    def detect_outliers(self, method: str = 'iqr') -> Dict[str, list]:
        """
        Detect outliers in numeric columns.
        
        Args:
            method (str): Method to detect outliers
                - 'iqr': Interquartile range method
                - 'zscore': Z-score method
                
        Returns:
            Dict: Dictionary with outlier information
        """
        if self.df is None:
            self.load_data()
        
        outliers = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if method == 'iqr':
            for col in numeric_cols:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_rows = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
                if len(outlier_rows) > 0:
                    outliers[col] = outlier_rows.index.tolist()
        
        elif method == 'zscore':
            for col in numeric_cols:
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outlier_rows = self.df[z_scores > 3]
                if len(outlier_rows) > 0:
                    outliers[col] = outlier_rows.index.tolist()
        
        return outliers


# Example usage (when run as main)
if __name__ == "__main__":
    # Initialize agent
    agent = DataAnalysisAgent()
    
    # Load data
    df = agent.load_data()
    print("\nDataset loaded successfully!")
    print(f"Shape: {df.shape}")
    
    # Handle missing values
    agent.handle_missing_values(strategy='drop')
    
    # Get summary
    summary = agent.get_dataset_summary()
    print("\nDataset Summary:")
    print(f"Shape: {summary['shape']}")
    print(f"Columns: {summary['columns']}")
    
    # Get descriptive statistics
    print("\nDescriptive Statistics:")
    print(agent.get_descriptive_statistics())
    
    # Detect outliers
    outliers = agent.detect_outliers(method='iqr')
    print("\nOutliers detected:")
    print(outliers)


