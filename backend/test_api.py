import requests
import os
import json

def test_process_application():
    """Test the /process-application/ endpoint with text input for job description."""
    # URL of the API endpoint
    url = "http://localhost:8000/process-application/"
    
    # Sample job description text
    job_description_text = """
    Job Description:
    
    We are seeking a skilled and experienced Software Engineer to join our dynamic team. 
    The ideal candidate will have a strong background in software development, 
    with a proven track record of designing, developing, and implementing 
    customized solutions.
    
    Key Responsibilities:
    
    - Design and develop high-quality software solutions
    - Write clean, maintainable, and efficient code
    - Troubleshoot and debug applications
    - Collaborate with cross-functional teams
    
    Qualifications:
    
    - Bachelor's degree in Computer Science or related field
    - 3+ years of experience in software development
    - Proficiency in one or more programming languages such as Java, Python, or JavaScript
    - Experience with databases and cloud services
    """
    
    # Path to the sample resume file
    resume_path = os.path.join(os.path.dirname(__file__), "resume.pdf")
    
    # Prepare the files to upload
    files = {
        "job_description_text": (None, job_description_text),
        "resume": open(resume_path, "rb")
    }
    
    try:
        # Make the POST request
        response = requests.post(url, files=files)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Print the results in a readable format
            print("API Response Status: SUCCESS")
            print("\n--- Tailored Content ---")
            
            tailored_content = data["tailored_content"]
            
            print("\nMatching Skills:")
            for skill in tailored_content["matching_skills"]:
                print(f"- {skill}")
            
            print("\nSkill Gaps:")
            for gap in tailored_content["skill_gaps"]:
                print(f"- {gap}")
            
            print("\nCover Letter Talking Points:")
            for point in tailored_content["cover_letter_points"]:
                print(f"- {point}")
            
            print("\nFit Summary:")
            print(tailored_content["fit_summary"])
            
            # Option to save the full response to a file
            with open("api_response.json", "w") as f:
                json.dump(data, f, indent=2)
            print("\nFull response saved to api_response.json")
            
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error during API request: {str(e)}")
    
    finally:
        # Close the files
        for file in files.values():
            if hasattr(file, 'close'):
                file.close()

if __name__ == "__main__":
    # First check if the API is running
    try:
        health_check = requests.get("http://localhost:8000/health")
        if health_check.status_code == 200:
            print("API is running. Starting test...\n")
            test_process_application()
        else:
            print("API is not responding correctly. Please make sure it's running.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API. Please start the server with:")
        print("  uvicorn main:app --reload") 