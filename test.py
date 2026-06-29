import sys

sys.path.append("student-dropout-agent")

from agents.prediction_agent import PredictionAgent
from agents.recommendation_agent import RecommendationAgent

# Initialize Agents
pred_agent = PredictionAgent()
pred_agent.load_model()

rec_agent = RecommendationAgent()

# Test Student
student_data = {
    'Age': 22,
    'Gender': 1,
    'Parental_Education': 0,
    'Family_Income_Level': 0,
    'Attendance_Percentage': 40,
    'Study_Hours_Per_Day': 1,
    'Sleep_Hours': 4,
    'Internet_Usage_Hours': 10,
    'Assignments_Completed': 20,
    'Previous_Grades': 35,
    'Class_Participation': 1,
    'Extracurricular_Activities': 0,
    'Stress_Level': 5,
    'Teacher_Feedback_Score': 1,
    'Absence_Days': 20
}

# Prediction
prediction = pred_agent.predict_dropout_risk(student_data)

print("\n========== PREDICTION ==========")
print(prediction)

# Recommendation
recommendation = rec_agent.generate_recommendations(
    student_data,
    prediction
)

print("\n========== RECOMMENDATION ==========")
print(recommendation)

from agents.report_agent import ReportAgent

report_agent = ReportAgent()

report = report_agent.generate_student_report(
    student_data,
    prediction,
    recommendation
)

print("\n========== REPORT ==========")
print(report)