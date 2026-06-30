"""
Report Agent
============
Purpose: Generate comprehensive student reports with predictions, risk factors, and recommendations.
Features: Fully integrated with the 15 features used in Prediction Agent.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReportAgent:
    """Agent responsible for generating comprehensive student reports based on 15 core features."""
    
    def __init__(self):
        """Initialize the Report Agent."""
        self.reports = []
        logger.info("ReportAgent initialized")
    
    def generate_student_report(
        self,
        student_data: Dict,
        prediction: Dict,
        recommendations: Dict,
        analysis_summary: Optional[Dict] = None
    ) -> Dict:
        """Generate a comprehensive student success report using all 15 training features."""
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
                'lifestyle_and_habits': self._build_lifestyle_and_habits(student_data),
                'risk_assessment': self._build_risk_assessment(prediction),
                'interventions': self._build_interventions(recommendations),
                'key_insights': self._extract_key_insights(student_data, prediction, recommendations),
                'recommendations_summary': recommendations.get('interventions', []),
                'support_services': recommendations.get('support_services', []),
                # report_agent.py ke andar line ~63 ke paas badlein:
                'next_steps': self._generate_next_steps(prediction.get('risk_level', 'Unknown')),                'report_status': 'Generated',
                'status': 'success'
            }
            
            # Store report in history
            self.reports.append(report)
            logger.info(f"Report generated successfully for student {student_id}")
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            return {
                'student_id': student_id,
                'report_status': 'Error',
                'status': 'error',
                'message': f'Report generation error: {str(e)}'
            }
    
    def _build_student_profile(self, student_data: Dict) -> Dict:
        """Build demographic profile section using training features."""
        return {
            'student_id': student_data.get('StudentID', 'Unknown'),
            'age': student_data.get('Age', 'N/A'),
            'gender': 'Male' if student_data.get('Gender') == 1.0 else 'Female' if student_data.get('Gender') == 0.0 else student_data.get('Gender', 'N/A'),
            'parental_education': student_data.get('Parental_Education', 'N/A'),
            'family_income_level': student_data.get('Family_Income_Level', 'N/A')
        }
    
    def _build_academic_performance(self, student_data: Dict, analysis_summary: Dict | None = None) -> Dict:
        """Build academic section using training features."""
        return {
            'previous_grades': student_data.get('Previous_Grades', 0),
            'attendance_percentage': student_data.get('Attendance_Percentage', 0),
            'assignments_completed': student_data.get('Assignments_Completed', 0),
            'class_participation': student_data.get('Class_Participation', 0),
            'teacher_feedback_score': student_data.get('Teacher_Feedback_Score', 0),
            'absence_days': student_data.get('Absence_Days', 0)
        }
        
    def _build_lifestyle_and_habits(self, student_data: Dict) -> Dict:
        """Build lifestyle section using the remaining training features."""
        return {
            'study_hours_per_day': student_data.get('Study_Hours_Per_Day', 0),
            'sleep_hours': student_data.get('Sleep_Hours', 0),
            'internet_usage_hours': student_data.get('Internet_Usage_Hours', 0),
            'extracurricular_activities': 'Yes' if student_data.get('Extracurricular_Activities') == 1.0 else 'No',
            'stress_level': student_data.get('Stress_Level', 0)
        }
    
    def _build_risk_assessment(self, prediction: Dict) -> Dict:
        """Safely handle prediction results and probabilities."""
        prob = prediction.get('dropout_probability', 0)
        if isinstance(prob, (int, float)):
            prob_str = f"{prob:.2%}" if prob <= 1.0 else f"{prob}%"
        else:
            prob_str = str(prob)

        conf = prediction.get('confidence_score', 0)
        conf_str = f"{conf:.2%}" if isinstance(conf, (int, float)) else str(conf)

        return {
            'risk_level': prediction.get('risk_level', 'Unknown'),
            'dropout_probability': prob_str,
            'confidence_score': conf_str,
            'assessment_date': datetime.now().isoformat(),
            'risk_description': self._get_risk_description(prediction.get('risk_level', 'Unknown'))
        }
    
    def _get_risk_description(self, risk_level: str) -> str:
        descriptions = {
            'No Risk': 'Student shows strong indicators for academic success with low dropout probability.',
            'Medium Risk': 'Student shows mixed indicators requiring targeted interventions and monitoring.',
            'High Risk': 'Student shows concerning indicators requiring immediate and intensive support.'
        }
        return descriptions.get(risk_level, 'Risk assessment not available')
    
    def _build_interventions(self, recommendations: Dict) -> Dict:
        return {
            'priority_level': recommendations.get('priority', 'Unknown'),
            'key_focus_areas': recommendations.get('key_focus_areas', []),
            'success_factors': recommendations.get('success_factors', []),
            'timeline': recommendations.get('timeline', {}),
            'recommended_services': recommendations.get('support_services', [])
        }
    
    def _extract_key_insights(self, student_data: Dict, prediction: Dict, recommendations: Dict) -> List[str]:
        """Extract smart text insights using the exact 15 feature names."""
        insights = []
        
        # Academic Check
        if student_data.get('Previous_Grades', 0) < 60:
            insights.append("Academic grades are currently below baseline requirements.")

        # Attendance Check
        if student_data.get('Attendance_Percentage', 0) < 75:
            insights.append("Low attendance detected. Requires urgent monitoring.")

        # Stress & Sleep Check
        if student_data.get('Stress_Level', 0) >= 7:
            insights.append("Critical stress levels reported by the student.")
        if student_data.get('Sleep_Hours', 0) < 6:
            insights.append("Lack of sleep might be impacting daily performance.")

        # Absence Check
        if student_data.get('Absence_Days', 0) > 8:
            insights.append(f"High risk due to accumulated absences ({student_data.get('Absence_Days')} days).")

        # Study Habits
        if student_data.get('Study_Hours_Per_Day', 0) < 2:
            insights.append("Daily self-study hours are below the average recommended threshold.")

        # Model Assessment
        insights.append(f"Overall assessment: {prediction.get('risk_level')} for dropout")        
        return insights
    
    from typing import Optional, List, Dict

    def _generate_next_steps(self, risk_level: Optional[str]) -> List[Dict]:
     if risk_level is None:
        risk_level = "Low Risk"

     if risk_level == 'High Risk':
        return [
            {'action': 'Schedule emergency advising appointment', 'timeline': 'Within 48 hours', 'responsible_party': 'Academic Advisor'},
            {'action': 'Enroll in intensive tutoring program', 'timeline': 'Within 1 week', 'responsible_party': 'Student Services'},
            {'action': 'Weekly progress monitoring tracker activation', 'timeline': 'Immediate', 'responsible_party': 'Success Team'}
        ]

     elif risk_level == 'Medium Risk':
        return [
            {'action': 'Schedule standard advising check-in', 'timeline': 'Within 1 week', 'responsible_party': 'Academic Advisor'},
            {'action': 'Recommend time-management workshop', 'timeline': 'Within 2 weeks', 'responsible_party': 'Student Coach'}
        ]

     else:
        return [
            {'action': 'Maintain current study roadmap', 'timeline': 'Ongoing', 'responsible_party': 'Student'}
        ]
    
    def export_report_to_json(self, report: Dict, output_path: str = None) -> str: # type: ignore
        try:
            json_report = json.dumps(report, indent=2, default=str)
            if output_path:
                with open(output_path, 'w') as f:
                    f.write(json_report)
                logger.info(f"Report successfully saved to {output_path}")
                return output_path
            return json_report
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            return ""

    def get_report_history(self, student_id: str = None) -> List[Dict]: # type: ignore
        if student_id:
            return [r for r in self.reports if r.get('student_id') == student_id]
        return self.reports


# --- CLEAN TEST PIPELINE MATCHING YOUR PREDICTION AGENT ---
if __name__ == "__main__":
    agent = ReportAgent()
    
    # 100% Matching 15 features 
    student_data = {
        'StudentID': 'S001',
        'Age': 21.0,
        'Gender': 1.0,
        'Parental_Education': 2.0,
        'Family_Income_Level': 2.0,
        'Attendance_Percentage': 72.5,  # Low attendance trigger
        'Study_Hours_Per_Day': 1.4,     # Low study hour trigger
        'Sleep_Hours': 5.5,             # Low sleep trigger
        'Internet_Usage_Hours': 3.5,
        'Assignments_Completed': 76.0,
        'Previous_Grades': 58.0,        # Academic warning trigger
        'Class_Participation': 8.0,
        'Extracurricular_Activities': 1.0,
        'Stress_Level': 8.0,            # High stress trigger
        'Teacher_Feedback_Score': 2.0,
        'Absence_Days': 11.0            # Absence trigger
    }
    
    prediction = {
        'risk_level': 'High Risk',
        'dropout_probability': 0.845,
        'confidence_score': 0.89
    }
    
    recommendations = {
        'priority': 'High',
        'interventions': [{'action': 'Parental meeting', 'priority': 'Critical'}],
        'support_services': ['Counseling', 'Academic Mentoring'],
        'key_focus_areas': ['Attendance', 'Mental Well-being'],
        'success_factors': ['Active extracurricular participation'],
        'timeline': {'Immediate': '1-7 Days'}
    }
    
    report = agent.generate_student_report(student_data, prediction, recommendations)
    print("\n✅ New Integrated Report Structure:")
    print(json.dumps(report, indent=2, default=str))