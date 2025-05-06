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
# Import prompts
from prompts import (
    DOCUMENT_PARSER_SYSTEM_PROMPT,
    RESUME_ANALYSIS_PROMPT,
    JOB_DESCRIPTION_ANALYSIS_PROMPT,
    RESUME_CUSTOMIZER_SYSTEM_PROMPT,
    RESUME_CUSTOMIZATION_PROMPT_TEMPLATE
)

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
MODEL_NAME = "gpt-4.1-nano"
OUTPUT_DIR = "output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load environment variables once at startup
load_dotenv(".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY must be set in the .env file")

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
        return OpenAI(api_key=OPENAI_API_KEY)
    except TypeError:
        # If that fails, try with more compatible parameters
        import httpx
        return OpenAI(
            api_key=OPENAI_API_KEY,
            http_client=httpx.Client() # Keep httpx if needed for your env proxy/setup
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

def call_ai_service(prompt: str, system_prompt: str, json_response: bool = True) -> Dict[str, Any]:
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

def analyze_document_with_ai(text: str, parse_type: str) -> Dict[str, Any]:
    """
    Parse text using AI with structured prompts.
    
    Args:
        text: Text content to parse
        parse_type: Type of content to parse ('resume' or 'job_description')
        
    Returns:
        Parsed content as a structured dictionary
    """
    prompts = {
        "resume": RESUME_ANALYSIS_PROMPT,
        "job_description": JOB_DESCRIPTION_ANALYSIS_PROMPT
    }

    system_prompt = DOCUMENT_PARSER_SYSTEM_PROMPT
    user_prompt = f"{prompts[parse_type]}\n\nDocument to parse:\n\n{text}"
    
    return call_ai_service(user_prompt, system_prompt)

#------------------------------------------------------------
# BUSINESS LOGIC FUNCTIONS
#------------------------------------------------------------

def extract_resume_data(text: str) -> Dict[str, Any]:
    """
    Parse resume text using AI to extract structured information.
    
    Args:
        text: Resume text content
        
    Returns:
        Structured resume data
    """
    with handle_errors("Resume parsing"):
        return analyze_document_with_ai(text, "resume")

def extract_job_description_data(text: str) -> Dict[str, str]:
    """
    Parse job description text using AI to extract key details.
    
    Args:
        text: Job description text
        
    Returns:
        Dictionary of job description sections
    """
    try:
        parsed_jd = analyze_document_with_ai(text, "job_description")
        
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

def get_resume_customization_prompt(resume_sections: Dict[str, Any], job_desc: Dict[str, str]) -> str:
    """
    Generate the prompt for resume customization based on resume and job description data.
    
    Args:
        resume_sections: Parsed resume sections
        job_desc: Parsed job description
        
    Returns:
        The complete prompt text
    """
    return RESUME_CUSTOMIZATION_PROMPT_TEMPLATE.format(
        resume_json=json.dumps(resume_sections, indent=2),
        job_description_json=json.dumps(job_desc, indent=2)
    )

def tailor_resume_for_job(resume_sections: Dict[str, Any], job_desc: Dict[str, str]) -> Dict[str, Any]:
    """
    Customize a resume based on a job description, following strict preservation and modification rules.

    Args:
        resume_sections: Parsed resume sections
        job_desc: Parsed job description

    Returns:
        Customized resume content
    """
    system_prompt = RESUME_CUSTOMIZER_SYSTEM_PROMPT
    prompt = get_resume_customization_prompt(resume_sections, job_desc)
    
    return call_ai_service(prompt, system_prompt)

def create_resume_filename(customized_resume: Dict[str, Any], job_description: Dict[str, str]) -> str:
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
        parsed_job_description = extract_job_description_data(job_description_text)
        
        # Read and parse resume
        resume_content = await resume.read()
        resume_text = extract_text_from_pdf(resume_content)
        parsed_resume = extract_resume_data(resume_text)
        
        # Generate customized resume content
        customized_resume = tailor_resume_for_job(parsed_resume, parsed_job_description)
        
        # Create filename for the resume
        custom_filename = create_resume_filename(customized_resume, parsed_job_description)
        
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
    

