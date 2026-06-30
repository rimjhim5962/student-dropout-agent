"""
Recommendation Agent
====================
Purpose: Generate personalized recommendations based on predicted dropout risk level.

Architecture:
- Analyzes student data and risk level
- Generates targeted recommendations
- Prioritizes interventions based on risk severity
- Provides actionable insights for academic support
"""

from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RecommendationAgent:
    """
    Agent responsible for generating personalized recommendations.
    
    This agent:
    1. Analyzes student risk profile
    2. Generates tailored recommendations
    3. Prioritizes interventions by risk level
    4. Provides actionable guidance
    """
    
    # Recommendation strategies by risk level
    RECOMMENDATIONS = {
        'No Risk': {
            'priority': 'Low',
            'interventions': [
                'Continue current study habits',
                'Maintain attendance and GPA',
                'Consider peer mentoring opportunities',
                'Explore advanced coursework'
            ],
            'support_services': [
                'Career counseling',
                'Scholarship opportunities',
                'Research assistantships'
            ]
        },
        'Medium Risk': {
            'priority': 'Medium',
            'interventions': [
                'Increase study hours gradually',
                'Schedule regular study groups',
                'Meet with academic advisor monthly',
                'Attend tutoring sessions',
                'Improve attendance to 85%+'
            ],
            'support_services': [
                'Tutoring services',
                'Academic coaching',
                'Study skills workshops',
                'Peer mentoring program'
            ]
        },
        'High Risk': {
            'priority': 'High',
            'interventions': [
                'Immediate meeting with academic advisor',
                'Enroll in intensive tutoring',
                'Create a structured study schedule (10+ hours/week)',
                'Daily attendance monitoring',
                'Consider course load reduction',
                'Seek counseling services'
            ],
            'support_services': [
                'Emergency tutoring services',
                'Financial aid consultation',
                'Mental health counseling',
                'Student success coaches',
                'Family consultation program',
                'Probation support program'
            ]
        }
    }
    
    def __init__(self):
        """Initialize the Recommendation Agent."""
        logger.info("RecommendationAgent initialized")
    
    def generate_recommendations(self, student_data: Dict, prediction: Dict) -> Dict:
        """
        Generate personalized recommendations based on student data and risk prediction.
        
        Args:
            student_data (Dict): Student information
            prediction (Dict): Prediction result containing risk level
            
        Returns:
            Dict: Comprehensive recommendations
        """
        risk_level = prediction.get('risk_level')
        
        if not risk_level or prediction.get('status') != 'success':
            logger.warning(f"Invalid prediction for {student_data.get('StudentID')}")
            return {
                'student_id': student_data.get('StudentID', 'Unknown'),
                'status': 'error',
                'message': 'Unable to generate recommendations - invalid prediction',
                'recommendations': []
            }
        
        # Get base recommendations for risk level
        base_recs = self.RECOMMENDATIONS.get(risk_level, {})
        
        # Customize based on student factors
        customized_recs = self._customize_recommendations(student_data, risk_level)
        
        result = {
            'student_id': student_data.get('StudentID', 'Unknown'),
            'risk_level': risk_level,
            'priority': base_recs.get('priority', 'Unknown'),
            'interventions': self._rank_interventions(
                student_data,
                risk_level,
                customized_recs.get('interventions', [])
            ),
            'support_services': base_recs.get('support_services', []),
            'key_focus_areas': self._identify_focus_areas(student_data, risk_level),
            'success_factors': self._identify_success_factors(student_data),
            'timeline': self._generate_timeline(risk_level),
            'status': 'success'
        }
        
        logger.info(f"Recommendations generated for {result['student_id']}: {risk_level}")
        return result
    
    def _customize_recommendations(self, student_data: Dict, risk_level: str) -> Dict:
        """
        Customize recommendations based on specific student characteristics.
        
        Args:
            student_data (Dict): Student information
            risk_level (str): Risk level
            
        Returns:
            Dict: Customized recommendations
        """
        customized = {'interventions': []}
        
        # Get base interventions
        base_interventions = self.RECOMMENDATIONS[risk_level]['interventions']
        customized['interventions'] = base_interventions.copy()
        
        # Add custom interventions based on specific factors
        grades = student_data.get('Previous_Grades', 0)
        attendance = student_data.get('Attendance_Percentage', 0)
        study_hours = student_data.get('Study_Hours_Per_Day', 0)
        stress = student_data.get('Stress_Level', 0)
        absence = student_data.get('Absence_Days', 0)
        
        # Grades-based customization
        if grades < 50:
            customized['interventions'].append(
                'Attend subject-specific tutoring sessions'
            )

        if attendance < 75:
            customized['interventions'].append(
                'Improve attendance through weekly monitoring'
            )

        if study_hours < 3:
            customized['interventions'].append(
                'Increase daily study hours gradually'
            )

        if stress >= 4:
            customized['interventions'].append(
                'Meet with student wellness counselor'
            )

        if absence > 10:
            customized['interventions'].append(
                'Track attendance and reduce absence days'
            )
        return customized
    
    def _rank_interventions(self, student_data: Dict, risk_level: str, interventions: List[str]) -> List[Dict]:
        """
        Rank interventions by urgency and impact.
        
        Args:
            student_data (Dict): Student information
            risk_level (str): Risk level
            interventions (List[str]): List of interventions
            
        Returns:
            List[Dict]: Ranked interventions with priority and timeline
        """
        ranked = []
        
        for idx, intervention in enumerate(interventions):
            # Assign priority based on risk level and position
            if risk_level == 'High Risk':
                priority = 'Immediate' if idx < 3 else 'High'
            elif risk_level == 'Medium Risk':
                priority = 'High' if idx < 2 else 'Medium'
            else:
                priority = 'Medium' if idx < 2 else 'Low'
            
            ranked.append({
                'action': intervention,
                'priority': priority,
                'estimated_timeline': self._estimate_timeline(intervention, risk_level)
            })
        
        return ranked
    
    def _estimate_timeline(self, intervention: str, risk_level: str) -> str:
        """
        Estimate implementation timeline for an intervention.
        
        Args:
            intervention (str): Intervention action
            risk_level (str): Risk level
            
        Returns:
            str: Timeline recommendation
        """
        if 'immediate' in intervention.lower() or 'emergency' in intervention.lower():
            return 'Within 48 hours'
        elif 'meeting' in intervention.lower() or 'advisor' in intervention.lower():
            return 'Within 1 week'
        elif 'enroll' in intervention.lower() or 'schedule' in intervention.lower():
            return 'Within 1-2 weeks'
        else:
            return 'Ongoing'
    
    def _identify_focus_areas(self, student_data: Dict, risk_level: str) -> List[str]:
        """
        Identify key focus areas for improvement.
        
        Args:
            student_data (Dict): Student information
            risk_level (str): Risk level
            
        Returns:
            List[str]: Focus areas ranked by importance
        """
        focus_areas = []
        
        # Evaluate each factor with fallback to original 15 features
        gpa = student_data.get('GPA')
        if gpa is None:
            grades = student_data.get('Previous_Grades')
            if grades is not None:
                gpa = float(grades) / 25.0
            else:
                gpa = 0.0
        if gpa < 2.5:
            focus_areas.append('Academic Performance')
        
        attendance = student_data.get('AttendanceRate')
        if attendance is None:
            att_pct = student_data.get('Attendance_Percentage')
            if att_pct is not None:
                attendance = float(att_pct) / 100.0
            else:
                attendance = 0.0
        if attendance < 0.85:
            focus_areas.append('Class Attendance')
        
        study_hours = student_data.get('StudyHours')
        if study_hours is None:
            sh_day = student_data.get('Study_Hours_Per_Day')
            if sh_day is not None:
                study_hours = float(sh_day) * 7.0
            else:
                study_hours = 0.0
        if study_hours < 21.0: # 3 hours per day * 7 days = 21 hours/week
            focus_areas.append('Study Habits')
        
        return focus_areas
    
    def _identify_success_factors(self, student_data: Dict) -> List[str]:
        """
        Identify existing strengths and success factors.
        
        Args:
            student_data (Dict): Student information
            
        Returns:
            List[str]: Success factors
        """
        success_factors = []
        if student_data.get('Previous_Grades', 0) >= 85:
            success_factors.append('Strong academic performance')

        if student_data.get('Attendance_Percentage', 0) >= 90:
            success_factors.append('Excellent attendance')

        if student_data.get('Study_Hours_Per_Day', 0) >= 5:
            success_factors.append('Consistent study habits')

        if student_data.get('Teacher_Feedback_Score', 0) >= 4:
            success_factors.append('Positive teacher feedback')
                
        return success_factors
    
    def _generate_timeline(self, risk_level: str) -> Dict:
        """
        Generate a timeline for recommended interventions.
        
        Args:
            risk_level (str): Risk level
            
        Returns:
            Dict: Timeline phases
        """
        if risk_level == 'High Risk':
            return {
                'Phase 1 - Emergency Response': '0-1 week',
                'Phase 2 - Intensive Support': '1-4 weeks',
                'Phase 3 - Stabilization': '4-8 weeks',
                'Phase 4 - Progress Monitoring': 'Ongoing'
            }
        elif risk_level == 'Medium Risk':
            return {
                'Phase 1 - Assessment': '0-2 weeks',
                'Phase 2 - Support Activation': '2-4 weeks',
                'Phase 3 - Progress Tracking': '4-12 weeks',
                'Phase 4 - Adjustment': 'As needed'
            }
        else:
            return {
                'Phase 1 - Reinforcement': '0-4 weeks',
                'Phase 2 - Growth Opportunities': '4-12 weeks',
                'Phase 3 - Continued Success': 'Ongoing'
            }


# Example usage (when run as main)
if __name__ == "__main__":
    # Initialize agent
    agent = RecommendationAgent()
    
    # Example student data and prediction
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
        'dropout_probability': 0.55
    }
    
    # Generate recommendations
    recommendations = agent.generate_recommendations(student_data, prediction)
    print("\nRecommendations Generated:")
    print(f"Student ID: {recommendations['student_id']}")
    print(f"Risk Level: {recommendations['risk_level']}")
    print(f"Priority: {recommendations['priority']}")
    print(f"Key Focus Areas: {recommendations['key_focus_areas']}")
