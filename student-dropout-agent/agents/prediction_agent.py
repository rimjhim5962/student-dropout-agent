"""
Prediction Agent
================
Purpose: Load trained Random Forest model and predict dropout risk for students using exact 15 features.
"""

import joblib
import pandas as pd
import numpy as np
import pickle
from typing import Dict, Optional, Tuple, List
import logging
import os
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PredictionAgent:
    """Agent responsible for predicting student dropout risk using a trained model."""
    
    REQUIRED_FEATURES = [
        'Age',
        'Gender',
        'Parental_Education',
        'Family_Income_Level',
        'Attendance_Percentage',
        'Study_Hours_Per_Day',
        'Sleep_Hours',
        'Internet_Usage_Hours',
        'Assignments_Completed',
        'Previous_Grades',
        'Class_Participation',
        'Extracurricular_Activities',
        'Stress_Level',
        'Teacher_Feedback_Score',
        'Absence_Days'
    ]
    
    def __init__(self, model_path: Optional[str] = None):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.model_path = model_path or os.path.join(self.base_dir, "models", "rf.pkl")
        self.model = None
        logger.info(f"PredictionAgent initialized with model path: {self.model_path}")
        
    def load_model(self) -> bool:
        """Load the pre-trained Random Forest model."""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found at: {self.model_path}")
                return False
                
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded successfully from {self.model_path}")
            return True
        except Exception as e:
            logger.exception("Failed to load model")
            return False
            
    def validate_student_data(self, student_data: Dict) -> Tuple[bool, str]:
        """Validate student data dynamically based on the 15 required features."""
        # 1. Check for required features
        for feature in self.REQUIRED_FEATURES:
            if feature not in student_data:
                return False, f"Missing required feature: {feature}"
        
        # 2. Corrected Validations matching the actual 15 features
        if not (15 <= student_data.get('Age', 0) <= 50):
            return False, "Age must be between 15 and 50"
        
        if not (0 <= student_data.get('Attendance_Percentage', 0) <= 100):
            return False, "Attendance_Percentage must be between 0 and 100"
            
        if not (0 <= student_data.get('Previous_Grades', 0) <= 100):
            return False, "Previous_Grades must be between 0 and 100"
        
        if student_data.get('Study_Hours_Per_Day', 0) < 0:
            return False, "Study_Hours_Per_Day cannot be negative"
            
        if student_data.get('Absence_Days', 0) < 0:
            return False, "Absence_Days cannot be negative"
        
        return True, ""
    
    def predict_dropout_risk(self, student_data: Dict) -> Dict:
        """Predict dropout risk for a student safely."""
        # Validate data
        is_valid, error_msg = self.validate_student_data(student_data)
        if not is_valid:
            logger.warning(f"Invalid student data: {error_msg}")
            return {
                'student_id': student_data.get('StudentID', 'Unknown'),
                'risk_level': None,
                'confidence_score': 0.0,
                'dropout_probability': None,
                'status': 'error',
                'message': error_msg
            }
        
        # Load model if not already loaded
        if self.model is None and not self.load_model():
            return {
                'student_id': student_data.get('StudentID', 'Unknown'),
                'risk_level': None,
                'confidence_score': 0.0,
                'dropout_probability': None,
                'status': 'error',
                'message': 'Model not available'
            }
        assert self.model is not None
        try:
            # Prepare features DataFrame dynamically in correct order
            features = pd.DataFrame([{feature: student_data[feature] for feature in self.REQUIRED_FEATURES}])
            
            # Predict
            predicted_class = self.model.predict(features)[0]

            probabilities = self.model.predict_proba(features)[0]

            class_index = list(self.model.classes_).index(predicted_class)

            risk_mapping = {
                0: "No Risk",
                1: "Medium Risk",
                2: "High Risk"
            }

            risk_level = risk_mapping[predicted_class]

            # Map classes to their probabilities safely
            class_indices = {c: i for i, c in enumerate(self.model.classes_)}
            prob_no_risk = float(probabilities[class_indices.get(0, 0)]) if 0 in class_indices else 0.0
            prob_medium_risk = float(probabilities[class_indices.get(1, 1)]) if 1 in class_indices else 0.0
            prob_high_risk = float(probabilities[class_indices.get(2, 2)]) if 2 in class_indices else 0.0

            # Calculate dropout probability as P(High Risk) + 0.5 * P(Medium Risk)
            dropout_prob = prob_high_risk + 0.5 * prob_medium_risk
            confidence_score = float(max(probabilities))
                        
            result = {
                'student_id': student_data.get('StudentID', 'Unknown'),
                'risk_level': risk_level,
                'confidence_score': confidence_score,
                'dropout_probability': dropout_prob,
                'status': 'success',
                'message': f'Prediction completed. Risk level: {risk_level}'
            }
            
            logger.info(f"Prediction for {result['student_id']}: {risk_level}")
            return result
        
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return {
                'student_id': student_data.get('StudentID', 'Unknown'),
                'risk_level': None,
                'confidence_score': 0.0,
                'dropout_probability': None,
                'status': 'error',
                'message': f'Prediction error: {str(e)}'
            }


# Test with the clean 15 features structure
if __name__ == "__main__":
    agent = PredictionAgent()
    # Mocking model structure to test code logic if file isn't loaded
    class MockModel:
        classes_ = [0, 1, 2]
        def predict(self, X): return [1]
        def predict_proba(self, X): return [[0.2, 0.7, 0.1]]
        
    agent.model = MockModel() 
    
    test_student = {
        'StudentID': 'S001',
        'Age': 21.0,
        'Gender': 1.0,
        'Parental_Education': 2.0,
        'Family_Income_Level': 2.0,
        'Attendance_Percentage': 89.7,
        'Study_Hours_Per_Day': 1.4,
        'Sleep_Hours': 8.6,
        'Internet_Usage_Hours': 2.4,
        'Assignments_Completed': 76.0,
        'Previous_Grades': 79.0,
        'Class_Participation': 8.0,
        'Extracurricular_Activities': 0.0,
        'Stress_Level': 5.0,
        'Teacher_Feedback_Score': 1.0,
        'Absence_Days': 6.0
    }
    
    print(agent.predict_dropout_risk(test_student))