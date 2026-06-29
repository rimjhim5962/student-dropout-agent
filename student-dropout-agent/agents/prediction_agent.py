"""
Prediction Agent
================
Purpose: Load trained Random Forest model and predict dropout risk for students.

Architecture:
- Loads pre-trained Random Forest model from pickle file
- Performs feature engineering and validation
- Predicts dropout risk categories (No Risk, Medium Risk, High Risk)
- Returns prediction confidence scores
"""

import joblib
import pandas as pd
import numpy as np
import pickle
from typing import Dict, Tuple, List
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PredictionAgent:
    """
    Agent responsible for predicting student dropout risk using a trained model.
    
    This agent:
    1. Loads pre-trained Random Forest model
    2. Validates student data
    3. Performs feature engineering
    4. Predicts dropout risk
    5. Returns risk categories and confidence scores
    """
    
    # Risk categories and thresholds
    RISK_CATEGORIES = {
        'No Risk': (0.0, 0.33),
        'Medium Risk': (0.33, 0.66),
        'High Risk': (0.66, 1.0)
    }
    
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
    
    def __init__(self, model_path: str = None):
        """
        Initialize the Prediction Agent.
        
        Args:
            model_path (str): Path to the trained model pickle file.
                             If None, uses default path.
        """
        self.model_path = "student-dropout-agent/models/rf.pkl"
        self.model = None
        self.scaler = None
        logger.info(f"PredictionAgent initialized with model path: {self.model_path}")
    
    def load_model(self) -> bool:
        """
        Load the pre-trained Random Forest model.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
            
        Raises:
            FileNotFoundError: If the model file is not found
        """
        try:
            if not os.path.exists(self.model_path):
                # Try finding in the current working directory relative path
                alt_path = "models/rf.pkl"
                if os.path.exists(alt_path):
                    self.model_path = alt_path
                else:
                    logger.warning(f"Model file not found at {self.model_path}")
                    logger.info("Creating placeholder model object for demonstration...")
                    # Create a placeholder model object for testing without actual pkl file
                    self.model = self._create_placeholder_model()
                    return True
            

            self.model = joblib.load(self.model_path)
            self.scaler = None
            
            logger.info(f"Model loaded successfully from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def _create_placeholder_model(self):
        """
        Create a placeholder model for demonstration purposes.
        
        Returns:
            Object: A mock model object that can make predictions
        """
        class PlaceholderModel:
            def __init__(self):
                self.classes_ = np.array([0, 1, 2])

            def predict_proba(self, X):
                # Return random probabilities for demonstration (3 classes)
                probs = np.random.rand(len(X), 3)
                probs = probs / probs.sum(axis=1, keepdims=True)
                return probs
            
            def predict(self, X):
                # Return random predictions
                return np.random.randint(0, 3, len(X))
        
        return PlaceholderModel()
    
    def validate_student_data(self, student_data: Dict) -> Tuple[bool, str]:
        """
        Validate student data before prediction.
        
        Args:
            student_data (Dict): Dictionary containing student information
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Check for required features
        for feature in self.REQUIRED_FEATURES:
            if feature not in student_data:
                return False, f"Missing required feature: {feature}"
        
        # Validate value ranges
        if not (15 <= student_data.get('Age', 0) <= 50):
            return False, "Age must be between 15 and 50"
        
        if not (0.0 <= student_data.get('GPA', 0) <= 4.0):
            return False, "GPA must be between 0.0 and 4.0"
        
        if not (0.0 <= student_data.get('AttendanceRate', 0) <= 1.0):
            return False, "AttendanceRate must be between 0.0 and 1.0"
        
        if student_data.get('PreviousFailures', 0) < 0:
            return False, "PreviousFailures cannot be negative"
        
        if student_data.get('StudyHours', 0) < 0:
            return False, "StudyHours cannot be negative"
        
        if student_data.get('TimeAtUniversity', 0) < 0:
            return False, "TimeAtUniversity cannot be negative"
        
        return True, ""
    
    def predict_dropout_risk(self, student_data: Dict) -> Dict:
        """
        Predict dropout risk for a student.
        
        Args:
            student_data (Dict): Dictionary containing student information
            
        Returns:
            Dict: Prediction results containing:
                - 'student_id': Student ID
                - 'risk_level': Risk category (No Risk, Medium Risk, High Risk)
                - 'confidence_score': Confidence score (0-1)
                - 'dropout_probability': Probability of dropout
                - 'status': 'success' or 'error'
                - 'message': Status message
        """
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
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            return {
                'student_id': student_data.get('StudentID', 'Unknown'),
                'risk_level': None,
                'confidence_score': 0.0,
                'dropout_probability': None,
                'status': 'error',
                'message': 'Model not available'
            }
        
        try:
            # Prepare features for prediction
            features = pd.DataFrame([{
                "Age": student_data['Age'],
                "Gender": student_data['Gender'],
                "Parental_Education": student_data['Parental_Education'],
                "Family_Income_Level": student_data['Family_Income_Level'],
                "Attendance_Percentage": student_data['Attendance_Percentage'],
                "Study_Hours_Per_Day": student_data['Study_Hours_Per_Day'],
                "Sleep_Hours": student_data['Sleep_Hours'],
                "Internet_Usage_Hours": student_data['Internet_Usage_Hours'],
                "Assignments_Completed": student_data['Assignments_Completed'],
                "Previous_Grades": student_data['Previous_Grades'],
                "Class_Participation": student_data['Class_Participation'],
                "Extracurricular_Activities": student_data['Extracurricular_Activities'],
                "Stress_Level": student_data['Stress_Level'],
                "Teacher_Feedback_Score": student_data['Teacher_Feedback_Score'],
                "Absence_Days": student_data['Absence_Days']
            }])
            # 1. Use model.predict(X) only for class index.
            class_index = self.model.predict(features)[0]

            # 2. Convert class index to label using model.classes_.
            predicted_class_label = self.model.classes_[class_index]

            risk_mapping = {
                0: "No Risk",
                1: "Medium Risk",
                2: "High Risk"
            }

            # 6. Ensure both risk_level and dropout_probability correspond to the same class index.
            risk_level = risk_mapping[predicted_class_label]

            # 3. dropout_probability must be taken from predict_proba(X) using the SAME predicted class index.
            # 4. Never use max(probabilities) as dropout_probability.
            probabilities = self.model.predict_proba(features)[0]
            dropout_prob = float(probabilities[class_index])

            # 5. confidence_score can be max(probabilities) if needed.
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
    
    def _categorize_risk(self, probability: float) -> str:
        """
        Categorize risk level based on probability.
        
        Args:
            probability (float): Dropout probability (0-1)
            
        Returns:
            str: Risk category
        """
        for category, (lower, upper) in self.RISK_CATEGORIES.items():
            if lower <= probability < upper:
                return category
        return "High Risk"  # Default to highest risk
    
    def predict_batch(self, students_data: List[Dict]) -> List[Dict]:
        """
        Predict dropout risk for multiple students.
        
        Args:
            students_data (List[Dict]): List of student data dictionaries
            
        Returns:
            List[Dict]: List of prediction results
        """
        results = []
        for student in students_data:
            result = self.predict_dropout_risk(student)
            results.append(result)
        
        logger.info(f"Batch prediction completed for {len(results)} students")
        return results


#Example usage (when run as main)
# if __name__ == "__main__":
#     # Initialize agent
#     agent = PredictionAgent()
#     agent.load_model()
    
#     # Example student data
#     student_data = {
#     'Age': 21.0,
#     'Gender': 1.0,
#     'Parental_Education': 2.0,
#     'Family_Income_Level': 2.0,
#     'Attendance_Percentage': 89.7,
#     'Study_Hours_Per_Day': 1.4,
#     'Sleep_Hours': 8.6,
#     'Internet_Usage_Hours': 2.4,
#     'Assignments_Completed': 76.0,
#     'Previous_Grades': 79.0,
#     'Class_Participation': 8.0,
#     'Extracurricular_Activities': 0.0,
#     'Stress_Level': 5.0,
#     'Teacher_Feedback_Score': 1.0,
#     'Absence_Days': 6.0
# }
    
#     # Make prediction
#     prediction = agent.predict_dropout_risk(student_data)
#     print("\nPrediction Result:")
#     print(prediction)
    
# result = agent.predict_dropout_risk(student_data)
# print(result)
