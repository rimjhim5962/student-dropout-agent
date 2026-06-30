import sys

sys.path.append("student-dropout-agent")

from agents.prediction_agent import PredictionAgent
from agents.recommendation_agent import RecommendationAgent

# Initialize Agents
pred_agent = PredictionAgent()
pred_agent.load_model()

rec_agent = RecommendationAgent()

# Test Student
student1 = {
    "Age": 18,
    "Gender": 1,
    "Parental_Education": 3,
    "Family_Income_Level": 2,
    "Attendance_Percentage": 98,
    "Study_Hours_Per_Day": 8,
    "Sleep_Hours": 8,
    "Internet_Usage_Hours": 1,
    "Assignments_Completed": 100,
    "Previous_Grades": 95,
    "Class_Participation": 10,
    "Extracurricular_Activities": 1,
    "Stress_Level": 1,
    "Teacher_Feedback_Score": 10,
    "Absence_Days": 0,
}

student2 = {
    "Age": 20,
    "Gender": 1,
    "Parental_Education": 0,
    "Family_Income_Level": 0,
    "Attendance_Percentage": 40,
    "Study_Hours_Per_Day": 1,
    "Sleep_Hours": 4,
    "Internet_Usage_Hours": 10,
    "Assignments_Completed": 10,
    "Previous_Grades": 35,
    "Class_Participation": 1,
    "Extracurricular_Activities": 0,
    "Stress_Level": 10,
    "Teacher_Feedback_Score": 2,
    "Absence_Days": 20,
}

# Prediction for Student 1
prediction1 = pred_agent.predict_dropout_risk(student1)
print("\n========== PREDICTION STUDENT 1 ==========")
print(prediction1)

# Prediction for Student 2
prediction2 = pred_agent.predict_dropout_risk(student2)
print("\n========== PREDICTION STUDENT 2 ==========")
print(prediction2)

# Recommendation for Student 2
recommendation = rec_agent.generate_recommendations(
    student2,
    prediction2
)

print("\n========== RECOMMENDATION STUDENT 2 ==========")
print(recommendation)

from agents.report_agent import ReportAgent

report_agent = ReportAgent()

report = report_agent.generate_student_report(
    student2,
    prediction2,
    recommendation
)

print("\n========== REPORT STUDENT 2 ==========")
print(report)