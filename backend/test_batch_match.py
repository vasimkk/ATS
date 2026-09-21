import requests
import json

def test_batch_match():
    url = "http://127.0.0.1:8000/api/analyze-ats-batch"
    
    # Mock candidate resume (Backend Developer)
    resume_text = """
    John Doe
    Email: john@example.com
    
    Work Experience
    Backend Developer at TechCorp
    - Built RESTful APIs using Python, FastAPI, and Django.
    - Optimized PostgreSQL database queries, reducing load times by 40%.
    - Deployed services to AWS using Docker and Kubernetes.
    - 4+ years of experience in backend engineering.
    
    Education
    Bachelor of Science in Computer Science
    """
    
    # List of 3 different Job Descriptions
    jds = [
        {
            "id": "job_1_backend",
            "text": """
            Looking for a Backend Developer.
            Must have 3+ years of experience.
            Required skills: Python, FastAPI, PostgreSQL, Docker, AWS.
            You will build and optimize RESTful web services.
            """
        },
        {
            "id": "job_2_frontend",
            "text": """
            Frontend Developer needed.
            Required skills: React, JavaScript, HTML, CSS, Tailwind.
            You will build beautiful UI components and manage state.
            """
        },
        {
            "id": "job_3_data_scientist",
            "text": """
            Data Scientist position.
            Required: Machine Learning, Scikit-Learn, Pandas, TensorFlow.
            Build predictive models and analyze large datasets.
            """
        }
    ]
    
    payload = {
        "resume_text": resume_text,
        "job_descriptions": jds
    }
    
    print("Sending batch request with 1 Resume and 3 Job Descriptions...")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        print("\n--- Ranked Matches ---")
        for idx, match in enumerate(data.get("ranked_matches", [])):
            print(f"Rank {idx+1}: {match['jd_id']} - Score: {match['overall_score']}% (Grade: {match['grade']})")
            
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")

if __name__ == "__main__":
    test_batch_match()
