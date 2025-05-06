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

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Import the JSON to PDF module
from .json_to_pdf import populate_template, read_latex_template, compile_latex_to_pdf
from .constants import DEFAULT_TEMPLATE_PATH
from .s3_utils import upload_file_to_s3

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

def generate_resume_pdf(resume_data, template_path=None, output_filename=None, verbose=False, upload_to_s3=True):
    """
    Generate a PDF resume from JSON data.
    
    Args:
        resume_data (dict): Resume data in JSON format
        template_path (str, optional): Path to LaTeX template. Defaults to template.tex.
        output_filename (str, optional): Name for output file. Defaults to generated UUID.
        verbose (bool, optional): Whether to show detailed LaTeX compilation output.
        upload_to_s3 (bool, optional): Whether to upload the PDF to S3. Defaults to True.
        
    Returns:
        tuple: (local_pdf_path, s3_url) - Path to the generated PDF file and S3 URL if uploaded
    """
    # Get template path
    if not template_path:
        template_path = Path(__file__).parent / "templates" / DEFAULT_TEMPLATE_PATH
    
    # Create unique filenames if not specified
    if not output_filename:
        # Generate a unique ID for the files
        unique_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        output_filename = f"resume_{unique_id}"
    
    # Ensure output filename doesn't have extension
    output_filename = output_filename.split('.')[0]
    
    # Define output paths
    latex_path = LATEX_OUTPUT_DIR / f"{output_filename}.tex"
    pdf_path = PDF_OUTPUT_DIR / f"{output_filename}.pdf"
    
    try:
        # Read template
        template = read_latex_template(template_path)
        
        # Convert resume data to LaTeX
        latex_content = populate_template(template, resume_data)
        
        # Write LaTeX to file
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Compile LaTeX to PDF with reduced output
        compile_success = compile_latex_to_pdf(
            str(latex_path),
            output_pdf=str(pdf_path),
            verbose=verbose
        )
        
        if compile_success:
            print(f"Successfully generated PDF: {pdf_path}")
            
            # Upload to S3 if requested and S3 bucket is configured
            s3_url = None
            if upload_to_s3:
                try:
                    # Get bucket name dynamically
                    bucket_name = get_s3_bucket_name()
                    logger.debug(f"Attempting to upload PDF to S3. S3_BUCKET_NAME={bucket_name}")
                    
                    # Check if S3 bucket name is configured
                    if not bucket_name:
                        logger.warning("S3_BUCKET_NAME environment variable not set. Skipping S3 upload.")
                    else:
                        # Create S3 object name for PDF
                        s3_object_name = f"resumes/{output_filename}.pdf"
                        logger.debug(f"S3 object name: {s3_object_name}")
                        
                        # Check if the PDF file exists
                        if not os.path.exists(str(pdf_path)):
                            logger.error(f"File to upload does not exist: {pdf_path}")
                        else:
                            logger.debug(f"File exists, size: {os.path.getsize(str(pdf_path))} bytes")
                            
                            # Upload the PDF file to S3
                            s3_url = upload_file_to_s3(
                                str(pdf_path),
                                bucket_name,
                                s3_object_name,
                                content_type='application/pdf'
                            )
                            
                            if s3_url:
                                logger.info(f"Successfully uploaded PDF to S3: {s3_url}")
                                
                                # Also upload the LaTeX file to S3
                                latex_object_name = f"latex/{output_filename}.tex"
                                logger.debug(f"Uploading LaTeX file to S3: {latex_object_name}")
                                
                                latex_s3_url = upload_file_to_s3(
                                    str(latex_path),
                                    bucket_name,
                                    latex_object_name,
                                    content_type='text/plain'
                                )
                                
                                if latex_s3_url:
                                    logger.info(f"Successfully uploaded LaTeX to S3: {latex_s3_url}")
                                else:
                                    logger.error("Failed to upload LaTeX to S3")
                            else:
                                logger.error("Failed to upload PDF to S3")
                except Exception as e:
                    logger.exception(f"Error uploading files to S3: {e}")
            else:
                logger.debug("S3 upload skipped (upload_to_s3=False)")
            
            return str(pdf_path), s3_url
        else:
            print("Failed to compile PDF")
            return None, None
            
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None, None


def save_resume_json(resume_data, filename=None, upload_to_s3=True):
    """
    Save resume JSON to a file.
    
    Args:
        resume_data (dict): Resume data in JSON format
        filename (str, optional): Output filename. Defaults to a generated UUID.
        upload_to_s3 (bool, optional): Whether to upload the JSON to S3. Defaults to True.
        
    Returns:
        tuple: (local_json_path, s3_url) - Path to the saved JSON file and S3 URL if uploaded
    """
    # Create JSON output directory
    json_output_dir = Path(__file__).parent.parent / "output" / "json"
    os.makedirs(json_output_dir, exist_ok=True)
    
    # Create filename if not specified
    if not filename:
        unique_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        filename = f"resume_{unique_id}.json"
    
    # Ensure filename has .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Create output path
    json_path = json_output_dir / filename
    
    try:
        # Write JSON to file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2)
        
        print(f"Successfully saved JSON: {json_path}")
        
        # Upload to S3 if requested and S3 bucket is configured
        s3_url = None
        if upload_to_s3:
            try:
                # Get bucket name dynamically
                bucket_name = get_s3_bucket_name()
                logger.debug(f"Attempting to upload JSON to S3. S3_BUCKET_NAME={bucket_name}")
                
                # Check if S3 bucket name is configured
                if not bucket_name:
                    logger.warning("S3_BUCKET_NAME environment variable not set. Skipping S3 upload.")
                else:
                    # Create S3 object name
                    s3_object_name = f"json/{filename}"
                    
                    # Upload the file to S3
                    s3_url = upload_file_to_s3(
                        str(json_path),
                        bucket_name,
                        s3_object_name,
                        content_type='application/json'
                    )
                    
                    if s3_url:
                        logger.info(f"Successfully uploaded JSON to S3: {s3_url}")
                    else:
                        logger.error("Failed to upload JSON to S3")
            except Exception as e:
                logger.exception(f"Error uploading JSON to S3: {e}")
        else:
            logger.debug("S3 upload skipped (upload_to_s3=False)")
        
        return str(json_path), s3_url
    except Exception as e:
        logger.error(f"Error saving JSON: {e}")
        return None, None


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