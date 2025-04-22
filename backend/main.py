from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
import os
import PyPDF2
import io
import json
import re
from typing import Dict, List, Any, Optional, Callable
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI
from pdf_generator.generate_pdf import generate_resume_pdf, save_resume_json
from datetime import datetime
import logging
from contextlib import contextmanager

#------------------------------------------------------------
# CONFIGURATION AND INITIALIZATION
#------------------------------------------------------------

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "deepseek-chat"
OUTPUT_DIR = "output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load environment variables once at startup
load_dotenv(".env")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY must be set in the .env file")

#------------------------------------------------------------
# CORE UTILITY FUNCTIONS
#------------------------------------------------------------

# Initialize OpenAI client once at startup
@lru_cache(maxsize=1)
def get_openai_client():
    """
    Get or create the OpenAI client with caching.
    
    Returns:
        OpenAI client instance
    """
    try:
        # First try with simplified parameters
        return OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    except TypeError:
        # If that fails, try with more compatible parameters
        import httpx
        return OpenAI(
            api_key=DEEPSEEK_API_KEY, 
            base_url="https://api.deepseek.com",
            http_client=httpx.Client()
        )

# Error handling context manager
@contextmanager
def handle_errors(operation_name: str, error_status: int = 500):
    """
    Context manager for standardized error handling.
    
    Args:
        operation_name: Name of the operation for error reporting
        error_status: HTTP status code to use for exceptions
    """
    try:
        yield
    except Exception as e:
        logger.error(f"{operation_name} error: {str(e)}")
        raise HTTPException(status_code=error_status, detail=f"{operation_name} error: {str(e)}")

def parse_json_response(content: str) -> Dict[str, Any]:
    """
    Parse JSON response from the AI model.
    
    Args:
        content: String content to parse as JSON
        
    Returns:
        Parsed JSON as a dictionary
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from the response if full content isn't valid JSON
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            extracted_json = content[json_start:json_end]
            return json.loads(extracted_json)
        raise ValueError("Failed to parse AI response as JSON")

def ai_request(prompt: str, system_prompt: str, json_response: bool = True) -> Dict[str, Any]:
    """
    Make a request to the DeepSeek AI API.
    
    Args:
        prompt: User prompt text
        system_prompt: System prompt text
        json_response: Whether to expect and parse a JSON response
        
    Returns:
        Response content as dictionary or string
    """
    with handle_errors("AI request"):
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} if json_response else None,
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        return parse_json_response(content) if json_response else content

#------------------------------------------------------------
# DOCUMENT PROCESSING FUNCTIONS
#------------------------------------------------------------

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: Binary PDF file content
        
    Returns:
        Extracted text from the PDF
    """
    with handle_errors("PDF extraction"):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def ai_parse_text(text: str, parse_type: str) -> Dict[str, Any]:
    """
    Parse text using DeepSeek AI with structured prompts.
    
    Args:
        text: Text content to parse
        parse_type: Type of content to parse ('resume' or 'job_description')
        
    Returns:
        Parsed content as a structured dictionary
    """
    prompts = {
        "resume": """Analyze this resume and extract the following information in JSON format:
- personal_info: Object containing name, email, phone, linkedin, github (if available)
- education: Array of objects, each with institution, degree, dates, location
- experience: Array of objects, each with company, title, dates, location, and an array of details/bullet points. For each bullet point, identify and extract any metrics or quantifiable achievements.
- skills: Object with categories as keys (e.g., 'Technical Skills', 'Soft Skills', 'Languages', 'Tools & Frameworks') and arrays of skills as values. IMPORTANT: Use proper category names without underscores or special characters.
- projects: Array of objects, each with name, technologies used, dates (if available), and an array of details/descriptions with measurable outcomes
- certifications: Array of objects with name, organization, and dates (if available)
- achievements: Array of notable accomplishments, especially those with metrics or measurable results

Look specifically for quantifiable achievements in both experience and projects sections that follow or could be adapted to the XYZ format ("Accomplished [X] as measured by [Y] by doing [Z]").

Ensure you handle various formats and layouts. Return a structured JSON object that accurately captures all resume information.
""",

        "job_description": """Analyze this job description and extract the following information in JSON format:
- job_title: The title of the position
- company: The company offering the position
- location: Where the job is located (if specified)
- responsibilities: Array of responsibilities or duties
- requirements: Array of required qualifications (split into technical and non-technical)
- qualifications: Array of educational or experience qualifications
- preferred_skills: Array of desired but not required skills
- key_performance_indicators: Any metrics or KPIs mentioned for success in the role
- technologies: Array of specific technologies, tools, or platforms mentioned
- keywords: Array of frequently used terms that appear to be important

Handle various job description formats and layouts. Return a structured JSON object that accurately captures all job information.
"""
    }

    system_prompt = "You are an expert document parser specialized in resume and job description analysis."
    user_prompt = f"{prompts[parse_type]}\n\nDocument to parse:\n\n{text}"
    
    return ai_request(user_prompt, system_prompt)

#------------------------------------------------------------
# BUSINESS LOGIC FUNCTIONS
#------------------------------------------------------------

def parse_resume(text: str) -> Dict[str, Any]:
    """
    Parse resume text using AI to extract structured information.
    
    Args:
        text: Resume text content
        
    Returns:
        Structured resume data
    """
    with handle_errors("Resume parsing"):
        return ai_parse_text(text, "resume")

def parse_job_description(text: str) -> Dict[str, str]:
    """
    Parse job description text using AI to extract key details.
    
    Args:
        text: Job description text
        
    Returns:
        Dictionary of job description sections
    """
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
        for key in ["responsibilities", "requirements", "qualifications", "preferred_skills"]:
            if key in parsed_jd:
                sections[key] = " ".join(parsed_jd[key]) if isinstance(parsed_jd[key], list) else parsed_jd[key]
        
        # Ensure we have at least some content
        if len(sections) < 2:  # Only has overview
            # Add a raw section with the full text as fallback
            sections["description"] = text
            
        return sections
    except Exception as e:
        logger.warning(f"AI job description parsing failed: {str(e)}. Using fallback parser.")
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
            return {k: " ".join(v) for k, v in sections.items()}
        except Exception as e2:
            logger.error(f"Fallback job description parsing failed: {str(e2)}")
            raise HTTPException(status_code=500, detail=f"Job description parsing failed: {str(e2)}")

def generate_tailored_content(job_desc: Dict[str, str], resume: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate tailored content using DeepSeek API.
    
    Args:
        job_desc: Parsed job description
        resume: Parsed resume
        
    Returns:
        Tailored content for job application
    """
    system_prompt = "You are an AI assistant specializing in job application analysis. IMPORTANT: Never include structural markers like '(X)', '(Y)', or '(Z)' in the final content - use these only as frameworks for creating the content."
    
    prompt = f"""
    I need to create tailored content for a job application. I'll provide the job description and resume details.
    
    JOB DESCRIPTION:
    {json.dumps(job_desc, indent=2)}
    
    RESUME:
    {json.dumps(resume, indent=2)}
    
    Based on the above job description and resume, conduct a detailed analysis following these guidelines:

    ### **Input Analysis Protocol**
    1. **Resume Analysis**  
       - Extract key achievements, skills, and metrics from the user's resume.  
       - Identify relevant projects, internships, and work experience.
       - Note technical skills/tools matching industry trends.

    2. **Job Description Analysis**  
       - Identify required and preferred qualifications (hard/soft skills).
       - Identify core responsibilities and performance metrics.
       - Identify recurring keywords/phrases.

    3. **Keyword Mapping**  
       - Create a mapping table to align user experience with job requirements, specifying match strength.

    Please provide:
    1. A comprehensive list of matching skills between the resume and job requirements
    2. A detailed list of skill gaps that should be addressed
    3. 3-5 talking points for a cover letter using the XYZ framework ("Accomplished [X] as measured by [Y] by doing [Z]")
       IMPORTANT: Do not include the actual markers "(X)", "(Y)", "(Z)" in the final output.
    4. A brief summary (max 100 words) evaluating the candidate's fit for this position
    
    Format your response as a structured JSON with the following fields:
    - matching_skills (array of objects with "skill" and "evidence" properties)
    - skill_gaps (array of objects with "skill" and "recommendation" properties)
    - cover_letter_points (array of strings using XYZ formula)
    - fit_summary (string)
    - keyword_analysis (object with "total_keywords", "keywords_matched", "match_percentage" properties)
    """
    
    return ai_request(prompt, system_prompt)

def customize_resume(resume_sections: Dict[str, Any], job_desc: Dict[str, str]) -> Dict[str, Any]:
    """
    Customize a resume based on a job description, following strict preservation and modification rules.
    
    Args:
        resume_sections: Parsed resume sections
        job_desc: Parsed job description
        
    Returns:
        Customized resume content
    """
    system_prompt = "You are an expert resume architect that customizes resumes to match job descriptions while following strict preservation and modification rules. IMPORTANT: Never include structural markers like '(X)', '(Y)', or '(Z)' in the final content - use these only as frameworks for creating the content. Also, use proper category names without underscores (e.g., 'Web Technologies' not 'web_technologies', 'Tools & Frameworks' not 'tools_frameworks'). For job titles, use ONLY the title without technology stacks in parentheses."
    
    prompt = f"""
    I need to customize a resume to better match a job description while following strict preservation and modification rules.
    
    RESUME:
    {json.dumps(resume_sections, indent=2)}
    
    JOB DESCRIPTION:
    {json.dumps(job_desc, indent=2)}
    
    **Task:** Create a tailored resume by analyzing the user's provided resume and job description. Use Google's XYZ formula ("Accomplished [X] as measured by [Y] by doing [Z]") to craft accomplishment-driven statements. Ensure the resume is ATS-compliant and aligned with industry best practices, including formatting and keyword optimization.

    ### **Input Analysis Protocol**
    1. **Resume Analysis**  
       - Extract:  
         - Key achievements, skills, and metrics from the user's resume.  
         - Relevant projects, internships, and work experience.  
         - Technical skills/tools matching industry trends.  

    2. **Job Description Analysis**  
       - Identify:  
         - Required and preferred qualifications (hard/soft skills).  
         - Core responsibilities and performance metrics.  
         - Recurring keywords/phrases.  

    3. **Keyword Mapping**  
       - Create a mapping table to align user experience with job requirements.

    ### **PRESERVATION RULES (DO NOT MODIFY THESE ELEMENTS)**:
    - Education Section (degrees, institutions, dates)
    - Company names in work experience
    - Employment dates
    
    ### **Content Generation Rules**
    1. **Professional Summary:**  
       Write a concise summary using XYZ format to highlight the user's top achievements relevant to the job.  
       *Template:*  
       "Experienced [Role/Industry] professional achieving [X1], [X2], and [X3], delivering measurable results ([Y1], [Y2]) through [Z1], [Z2]."
       IMPORTANT: Do NOT include framework markers like "(X)", "(Y)", "(Z)" in the final text.

    2. **Experience Section:**  
       - IMPORTANT: For job titles, use ONLY the title itself. DO NOT include technology stacks or other descriptions in parentheses next to the title.
       - Use XYZ bullets for each role:  
         *Template:* "[Action Verb] [Task], achieving [Metric] via [Method/Tool], addressing [JD Keyword]."  
         *Example:* "Streamlined onboarding process, reducing employee ramp-up time by 30% through implementation of an automated HRIS system."
         IMPORTANT: Do NOT include framework markers like "(X)", "(Y)", "(Z)" in the final text.
       - CRITICAL: Ensure that each bullet point is directly relevant to its associated job title. The achievements and responsibilities described must clearly align with what would be expected for that specific role.
       - For each job position, tailor the bullet points to reflect work that would be performed in that specific role - avoid generic points or descriptions that don't match the job title.

    3. **Projects Section:**  
       - Highlight projects using XYZ format:  
         *Template:* "Developed a [Solution/Product] to address [Problem/Situation], achieving [Result/Impact]."  
         IMPORTANT: Do NOT include framework markers like "(X)", "(Y)", "(Z)" in the final text.
         - Delete projects with <40% job description relevance
         - Modify kept projects to highlight job description keywords
         - Create 1-2 fictional projects if needed that use technologies from the job description

    4. **Skills Section:**  
       - Mirror keywords from the job description for ATS optimization. Categorize into:  
         - Technical Skills (programming languages, tools, platforms)  
         - Soft Skills (leadership, communication, etc.)  
         IMPORTANT: Use proper category names without underscores. For example, use "Web Technologies" not "web_technologies", "Tools & Frameworks" not "tools_frameworks", and "Soft Skills" not "soft_skills".

    5. **Job Title Adjustments:**
       - Change job titles in experience section to better align with the target role in the job description
       - IMPORTANT: Display job titles as simple text without any technology stack or descriptions in parentheses
       - When adjusting job titles, ensure that the corresponding bullet points remain appropriate and relevant to the new title. If necessary, also adjust the bullet points to maintain consistency with the job title.

    ### **Validation Checklist**
    - All bullets follow XYZ structure with quantifiable results (Y).  
    - 70%+ of job description keywords appear in the resume's first half.  
    - Metrics are specific and use percentages, dollar amounts, or time saved where possible.  
    - Formatting adheres to ATS standards.
    - Job titles do NOT include technology stacks in parentheses.
    - Each job title and its associated bullet points are properly aligned and relevant to each other.
    
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
    
    return ai_request(prompt, system_prompt)

def generate_resume_filename(customized_resume: Dict[str, Any], job_description: Dict[str, str]) -> str:
    """
    Generate a filename for the resume based on user name and job details.
    
    Args:
        customized_resume: The customized resume data
        job_description: The job description data
        
    Returns:
        A filename string for the resume
    """
    try:
        # Extract name from various possible structures
        person_name = (
            customized_resume.get('basics', {}).get('name') or
            customized_resume.get('personal_info', {}).get('name', 'Your Name')
        )
            
        # Extract job and company details
        company_name = job_description.get('company', '').strip()
        job_title = job_description.get('job_title', '').strip()

        # Extract from overview if not directly available
        if 'overview' in job_description:
            overview = job_description.get('overview', '')
            if not company_name:
                company_match = re.search(r'Company:\s*([^,\n]+)', overview)
                if company_match:
                    company_name = company_match.group(1).strip()
                    
            if not job_title:
                position_match = re.search(r'Position:\s*([^,\n]+)', overview)
                if position_match:
                    job_title = position_match.group(1).strip()

        # Clean and validate components
        def clean_text(text):
            return re.sub(r'[^\w]', '', text).lower() if text and text.lower() not in ['', 'notspecified', 'your name'] else ''

        clean_name = clean_text(person_name)
        clean_company = clean_text(company_name)
        clean_job = clean_text(job_title)

        # Generate filename based on available components
        if clean_name and clean_company:
            return f"{clean_name}-{clean_company}"
        elif clean_name and clean_job:
            return f"{clean_name}-{clean_job}"
        elif clean_name:
            return f"{clean_name}-resume"
        elif clean_company:
            return f"resume-for-{clean_company}"
        elif clean_job:
            return f"resume-{clean_job}"
        else:
            timestamp = datetime.now().strftime("%m%d%Y")
            return f"resume-{timestamp}"
            
    except Exception as e:
        logger.warning(f"Error creating custom filename: {e}")
        timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
        return f"resume-{timestamp}"

#------------------------------------------------------------
# FASTAPI APPLICATION SETUP
#------------------------------------------------------------

# Initialize FastAPI app
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

# Dependency to get OpenAI client
def get_client():
    return get_openai_client()

#------------------------------------------------------------
# API ENDPOINTS
#------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/process-application/", response_model=Dict[str, Any])
async def process_application(
    job_description_text: str = Form(..., description="Job description as text"),
    resume: UploadFile = File(...),
    client: OpenAI = Depends(get_client)
):
    """
    Process a job application by analyzing the job description and resume.
    
    - **job_description_text**: The job description as text
    - **resume**: A PDF file containing the applicant's resume
    
    Returns a JSON with tailored content and analysis.
    """
    with handle_errors("Application processing"):
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

@app.post("/customize-resume/", response_model=Dict[str, Any])
async def customize_resume_endpoint(
    job_description_text: str = Form(..., description="Job description as text"),
    resume: UploadFile = File(...),
    client: OpenAI = Depends(get_client)
):
    """
    Customize a resume based on a job description, following strict preservation and modification rules.
    
    - **job_description_text**: The job description as text
    - **resume**: A PDF file containing the applicant's resume
    
    Returns a JSON with the customized resume content and PDF path.
    """
    with handle_errors("Resume customization"):
        # Parse job description
        parsed_job_description = parse_job_description(job_description_text)
        
        # Read and parse resume
        resume_content = await resume.read()
        resume_text = extract_text_from_pdf(resume_content)
        parsed_resume = parse_resume(resume_text)
        
        # Generate customized resume content
        customized_resume = customize_resume(parsed_resume, parsed_job_description)
        
        # Create filename for the resume
        custom_filename = generate_resume_filename(customized_resume, parsed_job_description)
        
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
            logger.error(f"Error generating PDF: {str(e)}")
        
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

@app.get("/download-pdf/")
async def download_pdf(path: str, custom_filename: Optional[str] = None):
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
    with handle_errors("LaTeX file reading", error_status=404):
        # Check for invalid path
        if not path:
            raise ValueError("Invalid path: Path cannot be empty")
            
        # Convert from PDF path to LaTeX path if needed
        if path.endswith('.pdf'):
            # Extract the filename without extension
            filename = os.path.basename(path).replace('.pdf', '')
            # Construct the correct path to the LaTeX file in the latex directory
            latex_dir = os.path.join(os.path.dirname(os.path.dirname(path)), 'latex')
            path = os.path.join(latex_dir, f"{filename}.tex")
        
        logger.info(f"Looking for LaTeX file at: {path}")
        
        if not os.path.isfile(path):
            raise FileNotFoundError(f"LaTeX file not found at {path}")
        
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return Response(
            content=content,
            media_type="application/x-tex"
        )

# Mount static files directories for output
app.mount("/static-files", StaticFiles(directory=OUTPUT_DIR), name="static-files")

#------------------------------------------------------------
# APPLICATION ENTRY POINT
#------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
    
