import requests
import os
import json

def test_customize_resume():
    """Test the /customize-resume/ endpoint with text input for job description."""
    # URL of the API endpoint
    url = "http://localhost:8000/customize-resume/"
    
    # Sample job description text
    job_description_text = """
    Job Description: Senior Salesforce Developer
    
    We are seeking a skilled and experienced Salesforce Developer to join our dynamic team. 
    The ideal candidate will have a strong background in Salesforce development, 
    with a proven track record of designing, developing, and implementing 
    customized solutions within the Salesforce platform.
    
    Key Responsibilities:
    
    - Design and develop customized solutions within the Salesforce platform
    - Customize Salesforce applications using Apex, Visualforce, Lightning Components
    - Integrate Salesforce with other systems using APIs, middleware, and other integration tools
    - Manage data migration, data quality, and data governance within the Salesforce environment
    - Develop and execute test plans to ensure quality and functionality
    - Provide ongoing maintenance and support for Salesforce applications
    
    Qualifications:
    
    - Bachelor's degree in Computer Science, Information Technology, or related field
    - 3+ years of experience in Salesforce development
    - Proven experience with Apex, Visualforce, Lightning Components, and Salesforce APIs
    - Experience with Salesforce integrations using REST/SOAP APIs, middleware, and ETL tools
    - Salesforce Platform Developer I and II certifications are highly desirable
    - Strong understanding of Salesforce architecture and development best practices
    - Proficiency in Salesforce configuration, including workflows, process builder, and custom objects
    - Experience with Salesforce DX, Git, and CI/CD tools is a plus
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
            print("\n=== Customized Resume ===")
            customized = data["customized_resume"]
            
            # Print each section of the customized resume
            for section in ["personal_info", "education", "experience", "skills", "projects"]:
                if section in customized:
                    print(f"\n{section.upper()}:")
                    if isinstance(customized[section], str):
                        print(customized[section][:200] + "..." if len(customized[section]) > 200 else customized[section])
                    elif isinstance(customized[section], list):
                        for item in customized[section][:3]:  # Show first 3 items
                            print(f"- {item}")
                        if len(customized[section]) > 3:
                            print(f"... and {len(customized[section]) - 3} more items")
                    elif isinstance(customized[section], dict):
                        for key, value in list(customized[section].items())[:3]:
                            print(f"- {key}: {value[:100]}..." if isinstance(value, str) and len(value) > 100 else f"- {key}: {value}")
            
            if "modifications_summary" in customized:
                print("\nMODIFICATIONS SUMMARY:")
                print(customized["modifications_summary"][:300] + "..." if len(customized["modifications_summary"]) > 300 else customized["modifications_summary"])
            
            # Option to save the full response to a file
            with open("resume_customization_response.json", "w") as f:
                json.dump(data, f, indent=2)
            print("\nFull response saved to resume_customization_response.json")
            
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
            test_customize_resume()
        else:
            print("API is not responding correctly. Please make sure it's running.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API. Please start the server with:")
        print("  uvicorn main:app --reload") 