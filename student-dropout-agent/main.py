"""
Main Entry Point for Student Dropout Prevention System
======================================================
Purpose: Orchestrate all agents and coordinate the prediction workflow.

This module:
1. Initializes all agents
2. Manages the prediction pipeline
3. Coordinates inter-agent communication
4. Handles end-to-end workflows
"""

import sys
import logging
from typing import Dict, List
import json
from datetime import datetime

# Import agents
from agents.data_analysis_agent import DataAnalysisAgent
from agents.prediction_agent import PredictionAgent
from agents.recommendation_agent import RecommendationAgent
from agents.report_agent import ReportAgent
from mcp_server.mcp_server import MCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StudentSuccessSystem:
    """
    Main orchestrator for the Student Success & Dropout Prevention System.
    
    This class:
    1. Initializes all agents
    2. Coordinates multi-agent workflows
    3. Manages data flow between agents
    4. Provides unified interface to the system
    
    Architecture Overview:
    
    Data Flow:
        Raw Data
            ↓
        [Data Analysis Agent] → Dataset Summary
            ↓
        Student Data
            ↓
        [Prediction Agent] → Risk Prediction
            ↓
        [Recommendation Agent] → Recommendations
            ↓
        [Report Agent] → Final Report
            ↓
        [MCP Server] → External Access
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the Student Success System with all agents.
        
        Args:
            data_path (str): Path to the dataset (default: None, resolves relative to package)
        """
        logger.info("Initializing Student Success System...")
        
        # Initialize agents
        self.data_agent = DataAnalysisAgent(data_path)
        self.prediction_agent = PredictionAgent()
        self.recommendation_agent = RecommendationAgent()
        self.report_agent = ReportAgent()
        self.mcp_server = MCPServer()
        
        # Load data and model
        self.dataset = None
        self.analysis_summary = None
        
        logger.info("All agents initialized successfully")
    
    def initialize_system(self) -> bool:
        """
        Initialize system components (load data, models, etc.).
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Loading data...")
            self.dataset = self.data_agent.load_data()
            
            logger.info("Analyzing dataset...")
            self.data_agent.handle_missing_values(strategy='drop')
            self.analysis_summary = self.data_agent.get_dataset_summary()
            
            logger.info("Loading prediction model...")
            self.prediction_agent.load_model()
            
            logger.info("System initialization complete")
            return True
        
        except Exception as e:
            logger.error(f"System initialization failed: {str(e)}")
            return False
    
    def predict_single_student(self, student_data: Dict) -> Dict:
        """
        Complete workflow for predicting a single student.
        
        Args:
            student_data (Dict): Student information
            
        Returns:
            Dict: Consolidated result with prediction, recommendations, and report
        """
        logger.info(f"Processing student {student_data.get('StudentID')}")
        
        try:
            # Step 1: Make prediction
            logger.debug("Step 1: Getting dropout prediction...")
            prediction = self.prediction_agent.predict_dropout_risk(student_data)
            
            if prediction.get('status') != 'success':
                logger.warning(f"Prediction failed: {prediction.get('message')}")
                return prediction
            
            
            # Step 2: Generate recommendations
            logger.debug("Step 2: Generating recommendations...")
            recommendations = self.recommendation_agent.generate_recommendations(
                student_data,
                prediction
            )
            
            # Step 3: Generate report
            logger.debug("Step 3: Generating report...")
            report = self.report_agent.generate_student_report(
                student_data,
                prediction,
                recommendations,
                self.analysis_summary
            )
            
            # Step 4: Combine results
            result = {
                'workflow_status': 'success',
                'timestamp': datetime.now().isoformat(),
                'student_id': student_data.get('StudentID'),
                'prediction': prediction,
                'recommendations': recommendations,
                'report': report
            }
            
            logger.info(f"Processing complete for {student_data.get('StudentID')}")
            return result
        
        except Exception as e:
            logger.error(f"Error processing student: {str(e)}")
            return {
                'workflow_status': 'error',
                'message': str(e),
                'student_id': student_data.get('StudentID')
            }
    
    def predict_batch_students(self, students_data: List[Dict]) -> Dict:
        """
        Complete workflow for predicting multiple students.
        
        Args:
            students_data (List[Dict]): List of student data dictionaries
            
        Returns:
            Dict: Batch results with summary statistics
        """
        logger.info(f"Processing batch of {len(students_data)} students")
        
        batch_results = {
            'workflow_status': 'in_progress',
            'timestamp': datetime.now().isoformat(),
            'total_students': len(students_data),
            'results': [],
            'summary': {
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'no_risk_count': 0,
                'errors': 0
            }
        }
        
        # Process each student
        for i, student_data in enumerate(students_data, 1):
            logger.debug(f"Processing student {i}/{len(students_data)}")
            
            result = self.predict_single_student(student_data)
            batch_results['results'].append(result)
            
            # Update summary
            if result.get('workflow_status') == 'success':
                risk_level = result.get('prediction', {}).get('risk_level')
                if risk_level == 'High Risk':
                    batch_results['summary']['high_risk_count'] += 1
                elif risk_level == 'Medium Risk':
                    batch_results['summary']['medium_risk_count'] += 1
                else:
                    batch_results['summary']['no_risk_count'] += 1
            else:
                batch_results['summary']['errors'] += 1
        
        batch_results['workflow_status'] = 'completed'
        logger.info(f"Batch processing complete")
        
        return batch_results
    
    def get_system_stats(self) -> Dict:
        """
        Get system statistics.
        
        Returns:
            Dict: System statistics
        """
        stats = {
            'data_available': self.dataset is not None,
            'analysis_summary': self.analysis_summary,
            'reports_generated': len(self.report_agent.get_report_history()),
            'timestamp': datetime.now().isoformat()
        }
        return stats
    
    def display_summary(self):
        """Display system summary and usage instructions."""
        print("\n" + "="*70)
        print("  AI STUDENT SUCCESS & DROPOUT PREVENTION SYSTEM")
        print("="*70)
        print("\nSystem Components:")
        print("  [+] Data Analysis Agent     - Handles data loading and preprocessing")
        print("  [+] Prediction Agent        - Predicts dropout risk using ML models")
        print("  [+] Recommendation Agent    - Generates personalized recommendations")
        print("  [+] Report Agent            - Creates comprehensive reports")
        print("  [+] MCP Server              - Provides external API access")
        print("\nData Files:")
        print("  [Data] Dataset:              data/AI_Student_Success_Dropout_Dataset.csv")
        print("  [Model] Model:                models/rf.pkl")
        print("\nUsage:")
        print("  1. Launch Streamlit App:  streamlit run app/streamlit_app.py")
        print("  2. Run Main Script:       python main.py")
        print("  3. Access MCP Server:     python mcp_server/mcp_server.py")
        print("\nDocumentation:")
        print("  - See README.md for detailed information")
        print("  - Check agent modules for implementation details")
        print("="*70 + "\n")


def main():
    """Main function demonstrating system usage."""
    
    # Initialize system
    system = StudentSuccessSystem()
    system.display_summary()
    
    # Initialize components
    if not system.initialize_system():
        logger.error("Failed to initialize system")
        return
    
    # Example 1: Single student prediction
    print("\n" + "="*70)
    print("EXAMPLE 1: SINGLE STUDENT PREDICTION")
    print("="*70)
    
    single_student = {
   
    'StudentID': 'S004',
    'Age': 19,
    'Gender': 0,
    'Parental_Education': 0,
    'Family_Income_Level': 0,
    'Attendance_Percentage': 30,
    'Study_Hours_Per_Day': 0.5,
    'Sleep_Hours': 4,
    'Internet_Usage_Hours': 12,
    'Assignments_Completed': 5,
    'Previous_Grades': 25,
    'Class_Participation': 1,
    'Extracurricular_Activities': 0,
    'Stress_Level': 10,
    'Teacher_Feedback_Score': 1,
    'Absence_Days': 20
}
  
    
    result = system.predict_single_student(single_student)
    print(f"\nStudent: {result['student_id']}")
    print(f"Prediction Status: {result.get('prediction', {}).get('status')}")
    print(f"Risk Level: {result.get('prediction', {}).get('risk_level')}")
    print(f"Prediction confidence: {result.get('prediction', {}).get('dropout_probability'):.2%}")
    
    # Example 2: Batch prediction
    print("\n" + "="*70)
    print("EXAMPLE 2: BATCH STUDENT PREDICTION")
    print("="*70)
    
    batch_students = [
    {
        'StudentID': 'S002',
        'Age': 21,
        'Gender': 1,
        'Parental_Education': 2,
        'Family_Income_Level': 2,
        'Attendance_Percentage': 89.7,
        'Study_Hours_Per_Day': 1.4,
        'Sleep_Hours': 8.6,
        'Internet_Usage_Hours': 2.4,
        'Assignments_Completed': 76,
        'Previous_Grades': 79,
        'Class_Participation': 8,
        'Extracurricular_Activities': 0,
        'Stress_Level': 5,
        'Teacher_Feedback_Score': 1,
        'Absence_Days': 6
    },
    
       {
    'StudentID': 'S003',
    'Age': 20,
    'Gender': 0,
    'Parental_Education': 0,
    'Family_Income_Level': 0,
    'Attendance_Percentage': 40,
    'Study_Hours_Per_Day': 0.5,
    'Sleep_Hours': 4,
    'Internet_Usage_Hours': 12,
    'Assignments_Completed': 10,
    'Previous_Grades': 35,
    'Class_Participation': 1,
    'Extracurricular_Activities': 0,
    'Stress_Level': 10,
    'Teacher_Feedback_Score': 1,
    'Absence_Days': 20
}

]
    
    batch_result = system.predict_batch_students(batch_students)
    print(f"\nTotal Students: {batch_result['total_students']}")
    print(f"High Risk: {batch_result['summary']['high_risk_count']}")
    print(f"Medium Risk: {batch_result['summary']['medium_risk_count']}")
    print(f"No Risk: {batch_result['summary']['no_risk_count']}")
    print(f"Errors: {batch_result['summary']['errors']}")
    
    # Example 3: System statistics
    print("\n" + "="*70)
    print("EXAMPLE 3: SYSTEM STATISTICS")
    print("="*70)
    
    stats = system.get_system_stats()
    print(f"\nData Available: {stats['data_available']}")
    print(f"Reports Generated: {stats['reports_generated']}")
    print(f"Timestamp: {stats['timestamp']}")
    
    print("\n" + "="*70)
    print("Next Steps:")
    print("  1. Edit config/constitution.md to set system policies")
    print("  2. Launch Streamlit: streamlit run app/streamlit_app.py")
    print("  3. Train the ML model on your data")
    print("  4. Deploy agents to production")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
