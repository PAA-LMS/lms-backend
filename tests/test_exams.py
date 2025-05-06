import requests
import json
from datetime import datetime, timedelta
import os

BASE_URL = "http://localhost:8000"

def test_exam_system():
    # Test data
    lecturer_token = "YOUR_LECTURER_TOKEN"  # Replace with actual token
    student_token = "YOUR_STUDENT_TOKEN"    # Replace with actual token
    
    headers_lecturer = {
        "Authorization": f"Bearer {lecturer_token}",
        "Content-Type": "application/json"
    }
    
    headers_student = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    # 1. Create an exam
    print("\n1. Creating exam...")
    exam_data = {
        "title": "Test Exam",
        "description": "This is a test exam",
        "course_id": 1,
        "start_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=3)).isoformat(),
        "total_marks": 100
    }
    
    response = requests.post(
        f"{BASE_URL}/exams/",
        headers=headers_lecturer,
        json=exam_data
    )
    
    if response.status_code == 201:
        exam = response.json()
        exam_id = exam["id"]
        print(f"Exam created successfully with ID: {exam_id}")
    else:
        print(f"Failed to create exam: {response.text}")
        return
    
    # 2. Upload exam file
    print("\n2. Uploading exam file...")
    file_path = "test_exam.pdf"  # Create this file first
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            files = {"file": ("test_exam.pdf", f, "application/pdf")}
            response = requests.post(
                f"{BASE_URL}/exams/{exam_id}/upload",
                headers={"Authorization": f"Bearer {lecturer_token}"},
                files=files
            )
            print(f"File upload response: {response.text}")
    else:
        print("Test file not found")
    
    # 3. Submit exam answers
    print("\n3. Submitting exam answers...")
    submission_data = {
        "answers": {
            "q1": "Answer to question 1",
            "q2": "Answer to question 2"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/exams/{exam_id}/submit",
        headers=headers_student,
        json=submission_data
    )
    
    if response.status_code == 200:
        submission = response.json()
        print(f"Submission successful: {submission}")
    else:
        print(f"Failed to submit answers: {response.text}")
    
    # 4. Get exam submissions (as lecturer)
    print("\n4. Getting exam submissions...")
    response = requests.get(
        f"{BASE_URL}/exams/{exam_id}/submissions",
        headers=headers_lecturer
    )
    
    if response.status_code == 200:
        submissions = response.json()
        print(f"Found {len(submissions)} submissions")
    else:
        print(f"Failed to get submissions: {response.text}")

if __name__ == "__main__":
    test_exam_system() 