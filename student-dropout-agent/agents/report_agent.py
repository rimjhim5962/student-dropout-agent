"""
Report Agent
============
Purpose: Generate comprehensive student reports with predictions, risk factors, and recommendations.

Architecture:
- Consolidates data from other agents
- Generates structured student reports
- Exports reports in multiple formats (JSON, PDF ready)
- Tracks report generation history
"""

from typing import Dict, List
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReportAgent:
    """
    Agent responsible for generating comprehensive student reports.
    
    This agent:
    1. Consolidates data from analysis, prediction, and recommendation agents
    2. Generates structured reports
    3. Provides export functionality (JSON, etc.)
    4. Maintains report history
    """
    
    def __init__(self):
        """Initialize the Report Agent."""
        self.reports = []
        logger.info("ReportAgent initialized")
    
    def generate_student_report(
        self,
        student_data: Dict,
        prediction: Dict,
        recommendations: Dict,
        analysis_summary: Dict = None
    ) -> Dict:
        """
        Generate a comprehensive student success report.
        
        Args:
            student_data (Dict): Student information
            prediction (Dict): Prediction result
            recommendations (Dict): Recommendations
            analysis_summary (Dict): Optional data analysis summary
            
        Returns:
            Dict: Complete student report
        """
        student_id = student_data.get('StudentID', 'Unknown')
        
        try:
            report = {
                'report_metadata': {
                    'report_id': f"RPT_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'generated_at': datetime.now().isoformat(),
                    'student_id': student_id,
                    'report_version': '1.0'
                },
                'student_profile': self._build_student_profile(student_data),
                'academic_performance': self._build_academic_performance(student_data, analysis_summary),
                'risk_assessment': self._build_risk_assessment(prediction),
                'interventions': self._build_interventions(recommendations),
                'key_insights': self._extract_key_insights(student_data, prediction, recommendations),
                'recommendations_summary': recommendations.get('interventions', []),
                'support_services': recommendations.get('support_services', []),
                'next_steps': self._generate_next_steps(prediction.get('risk_level')),
                'report_status': 'Generated',
                'status': 'success'
            }
            
            # Store report
            self.reports.append(report)
            logger.info(f"Report generated for student {student_id}")
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                'student_id': student_id,
                'report_status': 'Error',
                'status': 'error',
                'message': f'Report generation error: {str(e)}'
            }
    
    def _build_student_profile(self, student_data: Dict) -> Dict:
        """
        Build student profile section of report.
        
        Args:
            student_data (Dict): Student information
            
        Returns:
            Dict: Student profile data
        """
        return {
            'student_id': student_data.get('StudentID', 'Unknown'),
            'age': student_data.get('Age', 'N/A'),
            'parental_education': student_data.get('Parental_Education', 'N/A'),
            'family_income_level': student_data.get('Family_Income_Level', 'N/A')
        }
    
    def _build_academic_performance(self, student_data: Dict, analysis_summary: Dict = None) -> Dict:
        """
        Build academic performance section of report.

        Args:
            student_data (Dict): Student information
            analysis_summary (Dict): Optional analysis summary

        Returns:
            Dict: Academic performance data
        """

        grades = student_data.get('Previous_Grades', 0)
        attendance = student_data.get('Attendance_Percentage', 0)

        return {
            'previous_grades': grades,
            'attendance_percentage': attendance,
            'study_hours_per_day': student_data.get('Study_Hours_Per_Day', 0),
            'assignments_completed': student_data.get('Assignments_Completed', 0),
            'absence_days': student_data.get('Absence_Days', 0)
        }
    
    def _build_risk_assessment(self, prediction: Dict) -> Dict:
        """
        Build risk assessment section of report.
        
        Args:
            prediction (Dict): Prediction result
            
        Returns:
            Dict: Risk assessment data
        """
        return {
            'risk_level': prediction.get('risk_level', 'Unknown'),
            'dropout_probability': f"{prediction.get('dropout_probability', 0):.2%}",
            'confidence_score': f"{prediction.get('confidence_score', 0):.2%}",
            'assessment_date': datetime.now().isoformat(),
            'risk_description': self._get_risk_description(prediction.get('risk_level'))
        }
    
    def _get_risk_description(self, risk_level: str) -> str:
        """Get description for risk level."""
        descriptions = {
            'No Risk': 'Student shows strong indicators for academic success with low dropout probability.',
            'Medium Risk': 'Student shows mixed indicators requiring targeted interventions and monitoring.',
            'High Risk': 'Student shows concerning indicators requiring immediate and intensive support.'
        }
        return descriptions.get(risk_level, 'Risk assessment not available')
    
    def _build_interventions(self, recommendations: Dict) -> Dict:
        """
        Build interventions section of report.
        
        Args:
            recommendations (Dict): Recommendations
            
        Returns:
            Dict: Interventions data
        """
        return {
            'priority_level': recommendations.get('priority', 'Unknown'),
            'key_focus_areas': recommendations.get('key_focus_areas', []),
            'success_factors': recommendations.get('success_factors', []),
            'timeline': recommendations.get('timeline', {}),
            'recommended_services': recommendations.get('support_services', [])
        }
    
    def _extract_key_insights(self, student_data: Dict, prediction: Dict, recommendations: Dict) -> List[str]:
        """
        Extract key insights from all data.
        
        Args:
            student_data (Dict): Student information
            prediction (Dict): Prediction result
            recommendations (Dict): Recommendations
            
        Returns:
            List[str]: Key insights
        """
        insights = []
        
        # Insight 1: GPA assessment
       # Insight 1: Academic Performance
        if student_data.get('Previous_Grades', 0) < 60:
            insights.append("Academic performance needs improvement")

        # Insight 2: Attendance
        if student_data.get('Attendance_Percentage', 0) < 75:
            insights.append("Attendance requires immediate attention")

        # Insight 3: Stress Level
        if student_data.get('Stress_Level', 0) >= 4:
            insights.append("High stress level detected")

        # Insight 4: Study Habits
        if student_data.get('Study_Hours_Per_Day', 0) < 3:
            insights.append("Study hours are below recommended level")

        # Insight 5: Absence Days
        if student_data.get('Absence_Days', 0) > 10:
            insights.append("High number of absence days observed")

        # Insight 6: Overall Risk
        insights.append(
            f"Overall assessment: {prediction.get('risk_level', 'Unknown')} for dropout"
        )

        return insights
    
    def _generate_next_steps(self, risk_level: str) -> List[Dict]:
        """
        Generate actionable next steps.
        
        Args:
            risk_level (str): Risk level
            
        Returns:
            List[Dict]: Next steps with timeline
        """
        next_steps = []
        
        if risk_level == 'High Risk':
            next_steps = [
                {
                    'action': 'Schedule emergency advising appointment',
                    'timeline': 'Within 48 hours',
                    'responsible_party': 'Academic Advisor'
                },
                {
                    'action': 'Enroll in intensive tutoring program',
                    'timeline': 'Within 1 week',
                    'responsible_party': 'Student Services'
                },
                {
                    'action': 'Complete study skills assessment',
                    'timeline': 'Within 2 weeks',
                    'responsible_party': 'Student Success Coach'
                },
                {
                    'action': 'Begin weekly progress monitoring',
                    'timeline': 'Ongoing',
                    'responsible_party': 'Academic Support Team'
                }
            ]
        elif risk_level == 'Medium Risk':
            next_steps = [
                {
                    'action': 'Schedule advising appointment',
                    'timeline': 'Within 1 week',
                    'responsible_party': 'Academic Advisor'
                },
                {
                    'action': 'Connect with tutoring services',
                    'timeline': 'Within 1-2 weeks',
                    'responsible_party': 'Student Services'
                },
                {
                    'action': 'Bi-weekly check-in calls',
                    'timeline': 'Ongoing',
                    'responsible_party': 'Student Success Coach'
                }
            ]
        else:
            next_steps = [
                {
                    'action': 'Continue current academic path',
                    'timeline': 'Ongoing',
                    'responsible_party': 'Academic Advisor'
                },
                {
                    'action': 'Explore enrichment opportunities',
                    'timeline': 'Next semester',
                    'responsible_party': 'Student Services'
                }
            ]
        
        return next_steps
    
    def export_report_to_json(self, report: Dict, output_path: str = None) -> str:
        """
        Export report to JSON format.
        
        Args:
            report (Dict): Report to export
            output_path (str): Optional output file path
            
        Returns:
            str: JSON report string or file path
        """
        try:
            json_report = json.dumps(report, indent=2, default=str)
            
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(json_report)
                logger.info(f"Report exported to {output_path}")
                return output_path
            
            return json_report
        
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            return ""
    
    def get_report_history(self, student_id: str = None) -> List[Dict]:
        """
        Retrieve report history.
        
        Args:
            student_id (str): Optional filter by student ID
            
        Returns:
            List[Dict]: List of reports
        """
        if student_id:
            return [r for r in self.reports if r.get('student_id') == student_id]
        return self.reports


# Example usage (when run as main)
if __name__ == "__main__":
    # Initialize agent
    agent = ReportAgent()
    
    # Example data
    student_data = {
        'StudentID': 'S001',
        'Age': 20,
        'GPA': 2.5,
        'AttendanceRate': 0.70,
        'PreviousFailures': 2,
        'StudyHours': 2.5,
        'TimeAtUniversity': 2,
        'ParentalSupport': 'Yes'
    }
    
    prediction = {
        'risk_level': 'Medium Risk',
        'status': 'success',
        'dropout_probability': 0.55,
        'confidence_score': 0.8
    }
    
    recommendations = {
        'risk_level': 'Medium Risk',
        'priority': 'Medium',
        'interventions': [
            {'action': 'Increase study hours', 'priority': 'High'},
            {'action': 'Meet with advisor', 'priority': 'High'}
        ],
        'support_services': ['Tutoring', 'Academic Coaching'],
        'key_focus_areas': ['Academic Performance', 'Study Habits'],
        'success_factors': ['Parental support'],
        'timeline': {'Phase 1': '0-2 weeks', 'Phase 2': '2-4 weeks'}
    }
    
    # Generate report
    report = agent.generate_student_report(student_data, prediction, recommendations)
    print("\nReport Generated:")
    print(json.dumps(report, indent=2, default=str))
