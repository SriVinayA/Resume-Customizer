from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
import os
import PyPDF2
import io
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from pdf_generator.generate_pdf import generate_resume_pdf, save_resume_json
from datetime import datetime

# Load environment variables
load_dotenv(".env")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY must be set in the .env file")

app = FastAPI(
    title="Job Application Processor",
    description="API for processing job applications using DeepSeek AI",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DeepSeek client
try:
    # First try with simplified parameters
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
except TypeError:
    # If that fails, try with more compatible parameters
    import httpx
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY, 
        base_url="https://api.deepseek.com",
        http_client=httpx.Client()
    )

def extract_text_from_pdf(pdf_file):
    """Extract text content from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {str(e)}")

def ai_parse_text(text, parse_type):
    """Parse text using DeepSeek AI with structured prompts"""
    try:
        prompts = {
            "resume": """Analyze this resume and extract the following information in JSON format:
- personal_info: Object containing name, email, phone, linkedin, github (if available)
- education: Array of objects, each with institution, degree, dates, location
- experience: Array of objects, each with company, title, dates, and an array of details/bullet points
- skills: Object with categories as keys and arrays of skills as values
- projects: Array of objects, each with name, technologies used, and an array of details/descriptions

Ensure you handle various formats and layouts. Return a structured JSON object that accurately captures all resume information.
""",

            "job_description": """Analyze this job description and extract the following information in JSON format:
- job_title: The title of the position
- company: The company offering the position
- location: Where the job is located (if specified)
- responsibilities: Array of responsibilities or duties
- requirements: Array of required qualifications
- qualifications: Array of educational or experience qualifications
- preferred_skills: Array of desired but not required skills

Handle various job description formats and layouts. Return a structured JSON object that accurately captures all job information.
"""
        }

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert document parser specialized in resume and job description analysis."},
                {"role": "user", "content": f"{prompts[parse_type]}\n\nDocument to parse:\n\n{text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        content = response.choices[0].message.content
        return json.loads(content)
    
    except json.JSONDecodeError:
        # If JSON parsing fails, attempt to extract JSON from the response
        try:
            content = response.choices[0].message.content
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                extracted_json = content[json_start:json_end]
                return json.loads(extracted_json)
        except:
            pass
        
        raise HTTPException(status_code=500, detail="Failed to parse AI response as JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI parsing error: {str(e)}")

def parse_job_description(text):
    """Parse job description text using AI to extract key details."""
    try:
        parsed_jd = ai_parse_text(text, "job_description")
        
        # Convert to format expected by downstream functions
        sections = {}
        
        # Create overview section with job title and company
        overview_parts = []
        if "job_title" in parsed_jd:
            overview_parts.append(f"Position: {parsed_jd['job_title']}")
        if "company" in parsed_jd:
            overview_parts.append(f"Company: {parsed_jd['company']}")
        if "location" in parsed_jd:
            overview_parts.append(f"Location: {parsed_jd['location']}")
        sections["overview"] = " ".join(overview_parts)
        
        # Add other sections
        if "responsibilities" in parsed_jd:
            sections["responsibilities"] = " ".join(parsed_jd["responsibilities"])
        if "requirements" in parsed_jd:
            sections["requirements"] = " ".join(parsed_jd["requirements"])
        if "qualifications" in parsed_jd:
            sections["qualifications"] = " ".join(parsed_jd["qualifications"])
        if "preferred_skills" in parsed_jd:
            sections["preferred_skills"] = " ".join(parsed_jd["preferred_skills"])
        
        # Ensure we have at least some content
        if len(sections) < 2:  # Only has overview
            # Add a raw section with the full text as fallback
            sections["description"] = text
            
        return sections
    except Exception as e:
        # Fallback to simple parsing if AI parsing fails
        print(f"AI job description parsing failed: {str(e)}. Using fallback parser.")
        try:
            # Simple fallback parsing
            sections = {}
            current_section = "overview"
            sections[current_section] = []
            
            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line is a section header
                if line.endswith(":") and len(line) < 50:  # Heuristic for section headers
                    current_section = line.rstrip(":")
                    sections[current_section] = []
                else:
                    sections[current_section].append(line)
                    
            # Convert lists to joined text
            for key in sections:
                sections[key] = " ".join(sections[key])
                
            return sections
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Job description parsing failed: {str(e2)}")

def parse_resume(text):
    """Parse resume text using AI to extract structured information."""
    try:
        return ai_parse_text(text, "resume")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

def generate_tailored_content(job_desc, resume):
    """Generate tailored content using DeepSeek API."""
    try:
        prompt = f"""
        I need to create tailored content for a job application. I'll provide the job description and resume details.
        
        JOB DESCRIPTION:
        {json.dumps(job_desc, indent=2)}
        
        RESUME:
        {json.dumps(resume, indent=2)}
        
        Based on the above job description and resume, please:
        1. Identify key skills and experiences from the resume that match the job requirements
        2. List any potential skill gaps
        3. Suggest 3-5 talking points for a cover letter that highlights the candidate's relevant experience
        4. Provide a brief summary of why this candidate is or isn't a good fit (max 100 words)
        
        Format your response as a structured JSON with the following fields:
        - matching_skills (array)
        - skill_gaps (array)
        - cover_letter_points (array)
        - fit_summary (string)
        """

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in job application analysis."},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        
        # Parse the JSON response from DeepSeek
        try:
            content = response.choices[0].message.content
            # Check if the content is already in JSON format
            try:
                parsed_content = json.loads(content)
                return parsed_content
            except json.JSONDecodeError:
                # If not proper JSON, extract it from the text
                # This is a fallback in case DeepSeek returns markdown or plain text
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    # If we can't find JSON, create a structured response based on the text
                    return {
                        "matching_skills": ["Unable to parse matching skills from AI response"],
                        "skill_gaps": ["Unable to parse skill gaps from AI response"],
                        "cover_letter_points": ["Unable to parse cover letter points from AI response"],
                        "fit_summary": "Unable to parse fit summary from AI response",
                        "raw_ai_response": content
                    }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

def customize_resume(resume_sections, job_desc):
    """
    Customize a resume based on a job description, following strict preservation and modification rules.
    
    Args:
        resume_sections: Parsed resume sections
        job_desc: Parsed job description
        
    Returns:
        Customized resume content
    """
    try:
        # Create a prompt for DeepSeek that enforces our preservation and modification rules
        prompt = f"""
        I need to customize a resume to better match a job description while following strict preservation and modification rules.
        
        RESUME:
        {json.dumps(resume_sections, indent=2)}
        
        JOB DESCRIPTION:
        {json.dumps(job_desc, indent=2)}
        
        PRESERVATION RULES (DO NOT MODIFY THESE ELEMENTS):
        - Education Section (degrees, institutions, dates)
        - Company names in work experience
        - Employment dates
        
        REQUIRED MODIFICATIONS:
        - Job Title: Change job titles in experience section to match the target role in the job description
        - Skills: Prioritize job description keywords, add missing relevant ones
        - Role Descriptions: Align bullet points with job description requirements
        - Projects: 
          a) Evaluate existing projects:
             - Delete projects with <40% job description relevance
             - Modify kept projects to highlight job description keywords
          b) Create 1-2 fictional projects if needed that:
             - Use technologies from the job description
             - Match the role seniority level
        
        CONTENT ADAPTATION RULES:
        1. Cross-Analysis:
           - Identify matching elements (keep unchanged)
           - Find resume-job gaps (modify to bridge)
           - Maintain natural language flow during modifications
        
        2. Experience Rewriting:
           - Maintain company/time facts
           - Change job titles to match the target role
           - Reorient role details to job description priorities
           - Add measurable achievements matching job description
           - Use job description verbs
           - Incorporate job description-specific technologies
           - Add quantifiable achievements matching job description scope
        
        3. Skill Optimization:
           - Map resume skills to job description requirements
           - Add missing job description keywords naturally
           - Remove irrelevant skills
        
        RESPONSE FORMAT:
        Generate a customized version of the resume that follows these rules. Return the result as a structured JSON with the following sections:
        - personal_info: Return as a structured object with fields for name, contact information, etc. (preserve from original)
        - education: Return as an array of education objects, each with institution, degree, location, and dates (preserve according to rules). 
          Do not modify the original education information provided, especially the institution names and dates.
        - experience: Return as an array of experience objects, each with company, title (modified to match job), dates, and details array
        - skills: Return as an object with categorized skills
        - projects: Return as an array of project objects
        - other: Any other sections, appropriately structured
        
        Also include a "modifications_summary" section that explains what changes were made and why.
        
        Make sure all object properties and array items are properly formatted with correct JSON syntax.
        """

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert resume architect that customizes resumes to match job descriptions while following strict preservation and modification rules."},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        
        # Parse the JSON response from DeepSeek
        try:
            content = response.choices[0].message.content
            # Check if the content is already in JSON format
            try:
                parsed_content = json.loads(content)
                return parsed_content
            except json.JSONDecodeError:
                # If not proper JSON, extract it from the text
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    # If we can't find JSON, create a structured response based on the text
                    return {
                        "error": "Unable to parse AI response as JSON",
                        "raw_ai_response": content
                    }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error customizing resume: {str(e)}")

@app.post("/process-application/", response_model=dict)
async def process_application(
    job_description_text: str = Form(..., description="Job description as text"),
    resume: UploadFile = File(...),
):
    """
    Process a job application by analyzing the job description and resume.
    
    - **job_description_text**: The job description as text
    - **resume**: A PDF file containing the applicant's resume
    
    Returns a JSON with tailored content and analysis.
    """
    # Parse job description
    parsed_job_description = parse_job_description(job_description_text)
    
    # Read and parse resume
    resume_content = await resume.read()
    resume_text = extract_text_from_pdf(resume_content)
    parsed_resume = parse_resume(resume_text)
    
    # Generate tailored content
    tailored_content = generate_tailored_content(parsed_job_description, parsed_resume)
    
    # Return the results
    return {
        "success": True,
        "tailored_content": tailored_content,
        "parsed_job_description": parsed_job_description,
        "parsed_resume": parsed_resume
    }

@app.post("/customize-resume/", response_model=dict)
async def customize_resume_endpoint(
    job_description_text: str = Form(..., description="Job description as text"),
    resume: UploadFile = File(...),
):
    """
    Customize a resume based on a job description, following strict preservation and modification rules.
    
    - **job_description_text**: The job description as text
    - **resume**: A PDF file containing the applicant's resume
    
    Returns a JSON with the customized resume content and PDF path.
    """
    # Parse job description
    parsed_job_description = parse_job_description(job_description_text)
    
    # Read and parse resume
    resume_content = await resume.read()
    resume_text = extract_text_from_pdf(resume_content)
    parsed_resume = parse_resume(resume_text)
    
    # Generate customized resume content
    customized_resume = customize_resume(parsed_resume, parsed_job_description)
    
    # Create filename based on priority system
    custom_filename = None
    try:
        # Extract components
        person_name = customized_resume.get('basics', {}).get('name', 'Your Name')
        company_name = parsed_job_description.get('company', '').strip()
        job_title = parsed_job_description.get('job_title', '').strip()

        # Handle placeholder values
        company_name = company_name if company_name and company_name.lower() not in ['', 'notspecified'] else None
        job_title = job_title if job_title and job_title.lower() not in ['', 'notspecified'] else None

        # Clean components
        def clean_text(text):
            return re.sub(r'[^\w]', '', text).lower() if text else ''

        clean_name = clean_text(person_name) if person_name and person_name.lower() != 'your name' else ''
        clean_company = clean_text(company_name)
        clean_job = clean_text(job_title)

        # Priority-based filename generation
        if clean_name and clean_company:
            custom_filename = f"{clean_name}-{clean_company}"
        elif clean_name and clean_job:
            custom_filename = f"{clean_name}-{clean_job}"
        elif clean_name:
            custom_filename = f"{clean_name}-resume"
        elif clean_company:
            custom_filename = f"resume-for-{clean_company}"
        elif clean_job:
            custom_filename = f"resume-{clean_job}"
        else:
            timestamp = datetime.now().strftime("%m%d%Y")
            custom_filename = f"resume-{timestamp}"
            
    except Exception as e:
        print(f"Error creating custom filename: {e}")
        timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
        custom_filename = f"resume-{timestamp}"
    
    # Generate PDF from the customized resume data
    pdf_path = None
    json_path = None
    try:
        # Save JSON for reference
        json_path = save_resume_json(customized_resume)
        
        # Generate PDF with reduced log output, using custom filename if available
        pdf_path = generate_resume_pdf(customized_resume, verbose=False, output_filename=custom_filename)
    except Exception as e:
        # Log the error but continue, as the JSON response is still useful
        print(f"Error generating PDF: {str(e)}")
    
    # Return the results - include customized resume and PDF path if available
    response = {
        "success": True,
        "customized_resume": customized_resume
    }
    
    if pdf_path:
        response["pdf_path"] = pdf_path
        if custom_filename:
            response["custom_filename"] = f"{custom_filename}.pdf"
    if json_path:
        response["json_path"] = json_path
        
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/download-pdf/")
async def download_pdf(path: str, custom_filename: str = None):
    """
    Download a PDF file by path.
    
    Args:
        path (str): Path to the PDF file
        custom_filename (str, optional): Custom filename for the download
        
    Returns:
        FileResponse: The PDF file as a downloadable attachment
    """
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Use provided custom filename or fallback to original filename
    filename = custom_filename if custom_filename else os.path.basename(path)
    
    return FileResponse(
        path=path,
        filename=filename,
        media_type="application/pdf"
    )

@app.get("/view-pdf/")
async def view_pdf(path: str):
    """
    View a PDF file by path.
    
    Args:
        path (str): Path to the PDF file
        
    Returns:
        FileResponse: The PDF file for viewing in the browser
    """
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        path=path,
        media_type="application/pdf"
    )

@app.get("/view-latex/")
async def view_latex(path: str):
    """
    Get the content of a LaTeX file by path.
    
    Args:
        path (str): Path to the LaTeX file
        
    Returns:
        Response: The LaTeX file content as text
    """
    # Check for invalid path
    if not path:
        raise HTTPException(status_code=400, detail="Invalid path: Path cannot be empty")
        
    # Convert from PDF path to LaTeX path if needed
    if path.endswith('.pdf'):
        # Extract the filename without extension
        filename = os.path.basename(path).replace('.pdf', '')
        # Construct the correct path to the LaTeX file in the latex directory
        latex_dir = os.path.join(os.path.dirname(os.path.dirname(path)), 'latex')
        path = os.path.join(latex_dir, f"{filename}.tex")
    
    print(f"Looking for LaTeX file at: {path}")
    
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"LaTeX file not found at {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return Response(
            content=content,
            media_type="application/x-tex"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading LaTeX file: {str(e)}")

# Mount static files directories for output
app.mount("/static-files", StaticFiles(directory="output"), name="static-files")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 