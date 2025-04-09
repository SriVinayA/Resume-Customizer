#!/usr/bin/env python3
"""
Test PDF Generation

This script tests the PDF generation functionality by loading a sample JSON resume
and generating a PDF file.

Run this script to test the PDF generation module:
    python test_pdf_generation.py
"""

import os
import json
import sys
from pathlib import Path

# Add the parent directory to sys.path to import the module
sys.path.append(str(Path(__file__).parent.parent))

# Import the PDF generator module
from pdf_generator.generate_pdf import generate_resume_pdf, save_resume_json

def test_pdf_generation():
    """Test the PDF generation functionality."""
    # Path to the sample JSON file (use the most recent customization response if available)
    json_path = Path(__file__).parent.parent / "resume_customization_response.json"
    
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}")
        print("Please run the customize-resume endpoint first to generate a sample JSON.")
        return False
    
    print(f"Loading resume data from {json_path}")
    
    # Load JSON data
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract customized resume data
        if "customized_resume" in data:
            resume_data = data["customized_resume"]
        else:
            resume_data = data
        
        print("Resume data loaded successfully.")
        
        # Generate PDF
        print("Generating PDF...")
        pdf_path = generate_resume_pdf(resume_data, output_filename="test_resume")
        
        if pdf_path:
            print(f"PDF generated successfully: {pdf_path}")
            print(f"Full path: {os.path.abspath(pdf_path)}")
            
            # Try to open the PDF
            if sys.platform == "darwin":  # macOS
                os.system(f"open {pdf_path}")
            elif sys.platform == "win32":  # Windows
                os.system(f"start {pdf_path}")
            elif sys.platform.startswith("linux"):  # Linux
                os.system(f"xdg-open {pdf_path}")
                
            return True
        else:
            print("Failed to generate PDF.")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_pdf_generation() 