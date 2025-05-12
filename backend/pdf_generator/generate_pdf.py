#!/usr/bin/env python3
"""
PDF Generation Integration Module

This module connects the FastAPI backend with the JSON-to-PDF conversion functionality.
It provides functions to generate PDF resumes from the JSON output of the 
customize-resume endpoint.

Usage:
    This module is intended to be imported and used by the FastAPI backend.
    
    Example:
        from pdf_generator.generate_pdf import generate_resume_pdf
        
        @app.post("/customize-resume/")
        async def customize_resume_endpoint(...):
            # Process and generate JSON response
            ...
            
            # Generate PDF
            pdf_path, s3_url = generate_resume_pdf(customized_resume)
            
            # Return both JSON and PDF path
            return {
                "success": True,
                "customized_resume": customized_resume,
                "pdf_path": pdf_path,
                "s3_url": s3_url
            }
"""

import os
import json
import tempfile
from pathlib import Path
import uuid
from datetime import datetime
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Tuple, Optional, Union

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Import the JSON to PDF module
from .json_to_pdf import populate_template, read_latex_template, compile_latex_to_pdf, json_to_pdf
from .constants import DEFAULT_TEMPLATE_PATH

# Import S3 utilities if available
try:
    from .s3_utils import upload_file_to_s3, parse_s3_url
except ImportError:
    # Fallback for when S3 utils are not available
    def upload_file_to_s3(*args, **kwargs):
        return None
    def parse_s3_url(*args, **kwargs):
        return None, None

# Directory for storing generated PDFs
PDF_OUTPUT_DIR = Path(__file__).parent.parent / "output" / "pdfs"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# Directory for storing LaTeX files
LATEX_OUTPUT_DIR = Path(__file__).parent.parent / "output" / "latex"
os.makedirs(LATEX_OUTPUT_DIR, exist_ok=True)

# Get S3 bucket name from environment variables
# We'll now get this dynamically each time we need it
def get_s3_bucket_name():
    """
    Get the S3 bucket name from environment variables, ensuring .env is loaded
    """
    # Try to load .env file if not already loaded
    load_dotenv()
    
    bucket_name = os.getenv("S3_BUCKET_NAME")
    logger.debug(f"S3 bucket name from environment: {bucket_name}")
    return bucket_name

def generate_resume_pdf(resume_data: Dict[str, Any], output_filename: Optional[str] = None, verbose: bool = False) -> Dict[str, str]:
    """
    Generate a PDF from the given resume data.
    
    Args:
        resume_data: Dictionary containing the resume data
        output_filename: Optional filename (without extension) for the output PDF
        verbose: Whether to log verbose output
        
    Returns:
        Dictionary with paths to the generated PDF (local and S3 if enabled)
    """
    # Use provided filename or generate a timestamp-based one
    if not output_filename:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"resume_{timestamp}"
    
    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Generate a PDF from the resume data
        output_path = f"output/{output_filename}.pdf"
        latex_path = f"output/{output_filename}.tex"
        json_to_pdf(resume_data, output_path, verbose)
        
        logger.info(f"Generated PDF at {output_path}")
        
        result = {
            "pdf_path": output_path,
            "custom_filename": f"{output_filename}.pdf"
        }
        
        # Try to upload to S3 if configured
        s3_bucket = os.getenv("S3_BUCKET_NAME")
        if s3_bucket:
            try:
                # Upload PDF to S3
                s3_path = f"resumes/{output_filename}.pdf"
                s3_url = upload_file_to_s3(output_path, s3_bucket, s3_path, content_type="application/pdf")
                if s3_url:
                    result["s3_pdf_url"] = s3_url
                    logger.info(f"Uploaded PDF to S3: {s3_url}")
                
                # Upload LaTeX file to S3 if it exists
                if os.path.exists(latex_path):
                    latex_s3_path = f"latex/{output_filename}.tex"
                    latex_s3_url = upload_file_to_s3(latex_path, s3_bucket, latex_s3_path, content_type="text/plain")
                    if latex_s3_url:
                        result["s3_latex_url"] = latex_s3_url
                        logger.info(f"Uploaded LaTeX file to S3: {latex_s3_url}")
                else:
                    logger.warning(f"LaTeX file not found at {latex_path}, cannot upload to S3")
            except Exception as e:
                logger.error(f"Error uploading files to S3: {str(e)}")
        
        return result
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return {}

def save_resume_json(resume_data: Dict[str, Any], output_filename: Optional[str] = None) -> Dict[str, str]:
    """
    Save the resume data as a JSON file.
    
    Args:
        resume_data: Dictionary containing the resume data
        output_filename: Optional filename (without extension) for the output JSON
        
    Returns:
        Dictionary with paths to the saved JSON (local and S3 if enabled)
    """
    # Use provided filename or generate a timestamp-based one
    if not output_filename:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"resume_{timestamp}"
    
    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Save JSON to file
        json_path = f"output/{output_filename}.json"
        with open(json_path, 'w') as f:
            json.dump(resume_data, f, indent=2)
        
        logger.info(f"Saved resume JSON to {json_path}")
        
        result = {
            "json_path": json_path
        }
        
        # Try to upload to S3 if configured
        s3_bucket = os.getenv("S3_BUCKET_NAME")
        if s3_bucket:
            try:
                # Upload JSON to S3
                s3_path = f"json/{output_filename}.json"
                s3_url = upload_file_to_s3(json_path, s3_bucket, s3_path, content_type="application/json")
                if s3_url:
                    result["s3_json_url"] = s3_url
                    logger.info(f"Uploaded JSON to S3: {s3_url}")
            except Exception as e:
                logger.error(f"Error uploading JSON to S3: {str(e)}")
        
        return result
    except Exception as e:
        logger.error(f"Error saving resume JSON: {str(e)}")
        return {}

if __name__ == "__main__":
    # Example usage (for testing)
    import json
    
    # Load example JSON data
    with open(Path(__file__).parent.parent / "resume_customization_response.json", 'r') as f:
        example_data = json.load(f)
    
    # Generate PDF
    pdf_path, s3_url = generate_resume_pdf(example_data)
    print(f"Generated PDF: {pdf_path}")
    if s3_url:
        print(f"S3 URL: {s3_url}") 