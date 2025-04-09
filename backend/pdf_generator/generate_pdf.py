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
            pdf_path = generate_resume_pdf(customized_resume)
            
            # Return both JSON and PDF path
            return {
                "success": True,
                "customized_resume": customized_resume,
                "pdf_path": pdf_path
            }
"""

import os
import json
import tempfile
from pathlib import Path
import uuid
from datetime import datetime

# Import the JSON to PDF module
from .json_to_pdf import populate_template, read_latex_template, compile_latex_to_pdf
from .constants import DEFAULT_TEMPLATE_PATH

# Directory for storing generated PDFs
PDF_OUTPUT_DIR = Path(__file__).parent.parent / "output" / "pdfs"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# Directory for storing LaTeX files
LATEX_OUTPUT_DIR = Path(__file__).parent.parent / "output" / "latex"
os.makedirs(LATEX_OUTPUT_DIR, exist_ok=True)


def generate_resume_pdf(resume_data, template_path=None, output_filename=None, verbose=False):
    """
    Generate a PDF resume from JSON data.
    
    Args:
        resume_data (dict): Resume data in JSON format
        template_path (str, optional): Path to LaTeX template. Defaults to template.tex.
        output_filename (str, optional): Name for output file. Defaults to generated UUID.
        verbose (bool, optional): Whether to show detailed LaTeX compilation output.
        
    Returns:
        str: Path to the generated PDF file
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
            return str(pdf_path)
        else:
            print("Failed to compile PDF")
            return None
            
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def save_resume_json(resume_data, filename=None):
    """
    Save resume JSON to a file.
    
    Args:
        resume_data (dict): Resume data in JSON format
        filename (str, optional): Output filename. Defaults to a generated UUID.
        
    Returns:
        str: Path to the saved JSON file
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
        return str(json_path)
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return None


if __name__ == "__main__":
    # Example usage (for testing)
    import json
    
    # Load example JSON data
    with open(Path(__file__).parent.parent / "resume_customization_response.json", 'r') as f:
        example_data = json.load(f)
    
    # Generate PDF
    pdf_path = generate_resume_pdf(example_data)
    print(f"Generated PDF: {pdf_path}") 