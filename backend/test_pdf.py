#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from pdf_generator.generate_pdf import generate_resume_pdf
from pdf_generator.json_to_pdf import populate_template, read_latex_template, compile_latex_to_pdf
from pdf_generator.constants import DEFAULT_TEMPLATE_PATH

def main():
    """Test the PDF generation functionality with detailed debugging."""
    try:
        # Get the JSON file path
        json_path = 'output/json/resume_20250318_153352_269547fe.json'
        
        # Check if file exists
        if not os.path.exists(json_path):
            print(f"Error: JSON file not found at {json_path}")
            return
        
        # Load the JSON data
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print(f"JSON loaded successfully from {json_path}")
        
        # Test each step individually to find the problem
        print("Step 1: Checking template path...")
        template_path = Path(__file__).parent / "pdf_generator" / "templates" / DEFAULT_TEMPLATE_PATH
        print(f"Template path: {template_path}")
        print(f"Template exists: {os.path.exists(template_path)}")
        
        print("\nStep 2: Reading LaTeX template...")
        try:
            template = read_latex_template(template_path)
            print("Template read successfully!")
            print(f"Template length: {len(template)} characters")
        except Exception as e:
            print(f"Error reading template: {e}")
            raise
        
        print("\nStep 3: Converting resume data to LaTeX...")
        try:
            latex_content = populate_template(template, data)
            print("LaTeX content generated successfully!")
            print(f"LaTeX content length: {len(latex_content)} characters")
        except Exception as e:
            print(f"Error generating LaTeX content: {e}")
            raise
        
        print("\nStep 4: Writing LaTeX to file...")
        latex_dir = Path(__file__).parent / "output" / "latex"
        os.makedirs(latex_dir, exist_ok=True)
        latex_path = latex_dir / "test_resume.tex"
        try:
            with open(latex_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            print(f"LaTeX file written successfully to: {latex_path}")
        except Exception as e:
            print(f"Error writing LaTeX file: {e}")
            raise
        
        print("\nStep 5: Compiling LaTeX to PDF...")
        pdf_dir = Path(__file__).parent / "output" / "pdfs"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = pdf_dir / "test_resume.pdf"
        try:
            compile_success = compile_latex_to_pdf(
                str(latex_path),
                output_pdf=str(pdf_path),
                verbose=True
            )
            print(f"Compilation result: {compile_success}")
            if compile_success:
                print(f"PDF generated successfully at: {pdf_path}")
                print(f"File exists: {os.path.exists(pdf_path)}")
            else:
                print("PDF compilation failed")
        except Exception as e:
            print(f"Error compiling PDF: {e}")
            raise
            
    except Exception as e:
        print(f"Error during PDF generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 