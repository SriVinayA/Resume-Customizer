import json
import re
import os
import sys
import argparse
import subprocess
import webbrowser
import glob
from .constants import (
    LATEX_SPECIAL_CHARS,
    SECTION_PATTERNS,
    EDUCATION_PATTERNS,
    DEFAULT_JSON_PATH,
    DEFAULT_TEMPLATE_PATH,
    DEFAULT_OUTPUT_PATH,
    EMAIL_PATTERN,
    LINKEDIN_PATTERN,
    GITHUB_PATTERN,
    PHONE_MIN_DIGITS
)

#------------------------------------------------------------------------------
# Utility Functions
#------------------------------------------------------------------------------

def escape_latex_special_chars(text):
    """
    Escape LaTeX special characters in the given text.
    
    Args:
        text (str): The text containing potentially special LaTeX characters
        
    Returns:
        str: Text with escaped LaTeX special characters
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        return str(text)
    
    # Process backslashes first to avoid double-escaping
    text = text.replace('\\', r'\textbackslash{}')
    
    # Then handle other special characters
    for char, replacement in LATEX_SPECIAL_CHARS.items():
        text = text.replace(char, replacement)
    
    return text

def is_email(text):
    """Check if text is likely an email address."""
    return '@' in text and re.search(EMAIL_PATTERN, text) is not None

def is_linkedin(text):
    """Check if text is likely a LinkedIn profile."""
    return LINKEDIN_PATTERN in text.lower()

def is_github(text):
    """Check if text is likely a GitHub profile."""
    return GITHUB_PATTERN in text.lower()

def is_phone(text):
    """Check if text is likely a phone number."""
    return any(c.isdigit() for c in text) and len([c for c in text if c.isdigit()]) >= PHONE_MIN_DIGITS

def ensure_url_protocol(url, protocol='https://'):
    """Ensure URL has a protocol prefix."""
    if url is None:
        return ''
    if not url.startswith(('http://', 'https://')):
        return f"{protocol}{url}"
    return url

#------------------------------------------------------------------------------
# File IO Functions
#------------------------------------------------------------------------------

def read_json_resume(file_path):
    """
    Read and parse the JSON resume file.
    
    Args:
        file_path (str): Path to the JSON resume file
        
    Returns:
        dict: Parsed resume data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Fix potentially malformed JSON
            content = file.read()
            if not content.strip().startswith('{'):
                content = '{' + content
            data = json.loads(content)
        
        # Extract resume data from the appropriate key
        if 'customized_resume' in data:
            return data['customized_resume']
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Resume JSON file not found: {file_path}")
        sys.exit(1)

def read_latex_template(file_path):
    """
    Read the LaTeX template file.
    
    Args:
        file_path (str): Path to the LaTeX template file
        
    Returns:
        str: Content of the template file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            template = file.read()
        return template
    except FileNotFoundError:
        print(f"LaTeX template file not found: {file_path}")
        sys.exit(1)

def write_latex_output(latex_content, output_path):
    """
    Write the populated LaTeX content to an output file.
    
    Args:
        latex_content (str): Complete LaTeX document content
        output_path (str): Path to write the output file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(latex_content)
        print(f"LaTeX resume successfully generated: {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

#------------------------------------------------------------------------------
# LaTeX Compilation Functions
#------------------------------------------------------------------------------

def compile_latex(tex_file, compiler="pdflatex", output_dir=None, continue_on_error=True, verbose=False, open_pdf=False, cleanup=False):
    """
    Compile a LaTeX file to PDF using the specified compiler.
    
    Args:
        tex_file (str): Path to the LaTeX file to compile
        compiler (str): LaTeX compiler to use ('pdflatex', 'xelatex', etc.)
        output_dir (str): Directory to store output files (default: same as tex_file)
        continue_on_error (bool): Whether to continue compilation despite errors
        verbose (bool): Whether to print detailed compilation output
        open_pdf (bool): Whether to open the PDF after successful compilation
        cleanup (bool): Whether to clean up auxiliary files after compilation
        
    Returns:
        bool: True if compilation succeeded, False otherwise
    """
    # Validate input file
    if not os.path.isfile(tex_file):
        print(f"Error: File {tex_file} not found.")
        return False
    
    # Get file paths
    tex_file = os.path.abspath(tex_file)
    base_dir = os.path.dirname(tex_file)
    filename = os.path.basename(tex_file)
    base_filename = os.path.splitext(filename)[0]
    
    # Set output directory
    if output_dir is None:
        output_dir = base_dir
    else:
        output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare compilation options
    interaction_mode = "nonstopmode" if continue_on_error else "errorstopmode"
    
    # Only print the compilation message if verbose is True
    if verbose:
        print(f"Compiling {filename} with {compiler}...")
    else:
        print(f"Compiling {base_filename}.tex to PDF...")
    
    # Map compiler names to latexmk options
    if compiler == "pdflatex":
        compiler_flag = "-pdf"
    elif compiler == "latex":
        compiler_flag = "-dvi"
    elif compiler == "xelatex":
        compiler_flag = "-xelatex"
    elif compiler == "lualatex":
        compiler_flag = "-lualatex"
    else:
        compiler_flag = "-pdf"  # Default
    
    # Additional flags to silence warnings
    quiet_flags = ["-silent"] if not verbose else []
    
    # Build the command
    cmd = [
        "latexmk", 
        compiler_flag,
        "-interaction=" + interaction_mode,
        "-file-line-error",
        f"-output-directory={output_dir}",
    ] + quiet_flags + [
        tex_file
    ]
    
    if verbose:
        print(f"Running: {' '.join(cmd)}")
    
    # Run the compilation
    try:
        # Capture output conditionally based on verbosity
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE if not verbose else None,
            stderr=subprocess.PIPE if not verbose else None,
            text=True
        )
        
        success = result.returncode == 0 or continue_on_error
        
        # Only show output on error or if verbose
        if not success and not verbose:
            print("Compilation failed. Error summary:")
            # Just print a summarized version of the error
            if result.stderr:
                error_lines = result.stderr.splitlines()
                for line in error_lines:
                    if "Error:" in line or "Fatal error:" in line:
                        print(line)
            
    except FileNotFoundError:
        print("Latexmk not found. Please install TeX Live, MiKTeX, or another LaTeX distribution.")
        return False
    
    # Check if PDF was generated
    pdf_path = os.path.join(output_dir, base_filename + ".pdf")
    if not os.path.exists(pdf_path):
        print(f"Compilation completed, but no PDF file was generated at {pdf_path}")
        return False
    
    if verbose:
        print(f"Successfully compiled {tex_file} to {pdf_path}")
    
    # Clean up auxiliary files if requested
    if cleanup:
        if verbose:
            print("Cleaning up auxiliary files...")
        # Define auxiliary file extensions to clean up
        aux_extensions = [
            '*.aux', '*.log', '*.out', '*.toc', '*.lof', '*.lot', 
            '*.bbl', '*.blg', '*.fls', '*.fdb_latexmk', '*.synctex.gz',
            '*.nav', '*.snm', '*.vrb', '*.run.xml', '*.bcf', '*.dvi'
        ]
        
        # Delete all auxiliary files
        for ext in aux_extensions:
            for file_path in glob.glob(os.path.join(output_dir, ext)):
                try:
                    if os.path.isfile(file_path) and not file_path.endswith('.pdf'):
                        os.remove(file_path)
                        if verbose:
                            print(f"Removed: {file_path}")
                except Exception as e:
                    if verbose:
                        print(f"Failed to remove {file_path}: {e}")
    
    # Open the PDF if requested
    if open_pdf and os.path.exists(pdf_path):
        if verbose:
            print(f"Opening PDF: {pdf_path}")
        try:
            webbrowser.open(f"file://{os.path.abspath(pdf_path)}")
        except Exception as e:
            print(f"Failed to open PDF: {e}")
    
    return True

def compile_latex_to_pdf(tex_file, output_pdf=None, compiler="pdflatex", verbose=False):
    """
    Wrapper function to compile a LaTeX file to PDF.
    
    Args:
        tex_file (str): Path to the LaTeX file to compile
        output_pdf (str, optional): Path for the output PDF. If None, uses the same name as tex_file.
        compiler (str): LaTeX compiler to use ('pdflatex', 'xelatex', etc.)
        verbose (bool): Whether to print detailed compilation output
        
    Returns:
        bool: True if compilation succeeded, False otherwise
    """
    if output_pdf is None:
        # Use the same name as the input, but with .pdf extension
        output_pdf = os.path.splitext(tex_file)[0] + ".pdf"
    
    # Get the output directory
    output_dir = os.path.dirname(output_pdf)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Compile the LaTeX file
    return compile_latex(
        tex_file,
        compiler=compiler,
        output_dir=output_dir,
        continue_on_error=True,
        verbose=verbose,
        open_pdf=False,
        cleanup=True
    )

#------------------------------------------------------------------------------
# Resume Section Formatting Functions
#------------------------------------------------------------------------------

def format_personal_info(personal_info):
    """
    Format personal information for LaTeX.
    
    Args:
        personal_info (dict or str): Personal information from JSON
        
    Returns:
        str: Formatted LaTeX for personal information section
    """
    # Handle personal_info as a structured object (new format)
    if isinstance(personal_info, dict):
        name = escape_latex_special_chars(personal_info.get('name', 'Your Name'))
        contact_items = []
        
        # Format phone with tel: protocol
        if 'phone' in personal_info:
            phone = escape_latex_special_chars(personal_info['phone'])
            phone_digits = phone.replace('-', '')
            contact_items.append(f"\\href{{tel:{phone_digits}}}{{{phone}}}")
        
        # Format email with mailto: protocol and underline
        if 'email' in personal_info:
            email = escape_latex_special_chars(personal_info['email'])
            contact_items.append(f"\\href{{mailto:{email}}}{{\\underline{{{email}}}}}")
        
        # Format LinkedIn with proper URL and underline
        if 'linkedin' in personal_info:
            linkedin = escape_latex_special_chars(personal_info['linkedin'])
            linkedin_url = ensure_url_protocol(linkedin)
            contact_items.append(f"\\href{{{linkedin_url}}}{{\\underline{{{linkedin}}}}}")
        
        # Format GitHub with proper URL and underline
        if 'github' in personal_info and personal_info['github'] is not None:
            github = escape_latex_special_chars(personal_info['github'])
            github_url = ensure_url_protocol(github)
            contact_items.append(f"\\href{{{github_url}}}{{\\underline{{{github}}}}}")
        
        # Format contact info with pipe separators
        contact_info = ' $|$ '.join(contact_items)
        
        return f"""\\begin{{center}}
\\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{1pt}}
\\small {contact_info}
\\end{{center}}"""
    
    # Handle personal_info as a string (legacy format)
    elif isinstance(personal_info, str):
        # Parse the personal info string
        parts = personal_info.strip().split('|')
        if len(parts) >= 1:
            # Format name from first part
            name_parts = parts[0].strip().split()
            name = escape_latex_special_chars(
                ' '.join(name_parts[0:2]) if len(name_parts) >= 2 else parts[0].strip()
            )
            
            # Format contact info with hyperlinks
            formatted_parts = []
            for part in parts[1:]:
                part = part.strip()
                escaped_part = escape_latex_special_chars(part)
                
                if is_email(part):
                    formatted_parts.append(f"\\href{{mailto:{escaped_part}}}{{\\underline{{{escaped_part}}}}}")
                elif is_linkedin(part):
                    linkedin_url = ensure_url_protocol(part)
                    formatted_parts.append(f"\\href{{{linkedin_url}}}{{\\underline{{{escaped_part}}}}}")
                elif is_github(part):
                    github_url = ensure_url_protocol(part)
                    formatted_parts.append(f"\\href{{{github_url}}}{{\\underline{{{escaped_part}}}}}")
                elif is_phone(part):
                    phone_digits = ''.join([c for c in part if c.isdigit()])
                    formatted_parts.append(f"\\href{{tel:{phone_digits}}}{{{escaped_part}}}")
                else:
                    formatted_parts.append(escaped_part)
            
            contact_info = ' $|$ '.join(formatted_parts)
            
            return f"""\\begin{{center}}
\\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{1pt}}
\\small {contact_info}
\\end{{center}}"""
    
    # Default return if format is unexpected
    return """\\begin{center}
\\textbf{\\Huge \\scshape Your Name} \\\\ \\vspace{1pt}
\\small phone $|$ email $|$ linkedin $|$ github
\\end{center}"""

def format_education(education):
    """
    Format education section for LaTeX.
    
    Args:
        education (list or str): Education information from JSON
        
    Returns:
        str: Formatted LaTeX for education section
    """
    edu_latex = "\\section{Education}\n\\resumeSubHeadingListStart\n"
    
    # Handle education as a list of dictionaries (new format)
    if isinstance(education, list) and education:
        for entry in education:
            if isinstance(entry, dict):
                # Get the institution name, clean up if needed
                institution = entry.get('institution', '')
                location = entry.get('location', '')
                
                # Add null checks before using endswith
                if institution and location and institution.endswith(location):
                    # Remove the location from the institution if it's duplicated
                    institution = institution.replace(location, '').strip()
                
                institution = escape_latex_special_chars(institution)
                location = escape_latex_special_chars(location)
                degree = escape_latex_special_chars(entry.get('degree', ''))
                dates = escape_latex_special_chars(entry.get('dates', ''))
                
                edu_latex += format_education_entry(institution, location, degree, dates)
                
                # Add descriptions/achievements if available
                if 'details' in entry and isinstance(entry['details'], list) and entry['details']:
                    edu_latex += "\\resumeItemListStart\n"
                    for detail in entry['details']:
                        detail_text = escape_latex_special_chars(detail)
                        edu_latex += f"\\resumeItem{{{detail_text}}}\n"
                    edu_latex += "\\resumeItemListEnd\n"
    
    # Handle education as a string (legacy format)
    elif isinstance(education, str) and education.strip():
        # Parse using regex patterns from constants
        parts = re.split(EDUCATION_PATTERNS['institution_split'], education)
        
        institutions = []
        # Extract all universities/institutes
        for i, part in enumerate(parts):
            if part in ["University", "Institute", "College"]:
                if i > 0 and i+1 < len(parts):
                    inst = parts[i-1].strip() + part + parts[i+1].split("Master")[0].split("Bachelor")[0].strip()
                    institutions.append(inst.strip())
        
        # Extract other information
        locations = re.findall(EDUCATION_PATTERNS['location'], education)
        degrees = re.findall(EDUCATION_PATTERNS['degree'], education)
        dates = re.findall(EDUCATION_PATTERNS['dates'], education)
        
        # Create entries from extracted data
        edu_entries = []
        for i in range(max(len(institutions), len(locations), len(degrees), len(dates))):
            entry = {
                'institution': institutions[i] if i < len(institutions) else '',
                'location': locations[i] if i < len(locations) else '',
                'degree': degrees[i] if i < len(degrees) else '',
                'dates': dates[i] if i < len(dates) else ''
            }
            if entry['institution'] and (entry['degree'] or entry['dates']):
                edu_entries.append(entry)
        
        # Format entries in LaTeX
        for entry in edu_entries:
            institution = escape_latex_special_chars(entry['institution'])
            location = escape_latex_special_chars(entry['location'])
            degree = escape_latex_special_chars(entry['degree'])
            dates = escape_latex_special_chars(entry['dates'])
            
            edu_latex += format_education_entry(institution, location, degree, dates)
    
    edu_latex += "\\resumeSubHeadingListEnd\n"
    return edu_latex

def format_education_entry(institution, location, degree, dates):
    """Helper function to format a single education entry."""
    # Ensure none of the values are "None" literals
    institution = "" if institution is None else institution
    location = "" if location is None else location
    degree = "" if degree is None else degree
    dates = "" if dates is None else dates
    
    return f"""\\resumeSubheading
{{{institution}}}{{{location}}}
{{{degree}}}{{{dates}}}
"""

def format_experience(experience):
    """
    Format experience section for LaTeX.
    
    Args:
        experience (list): List of experience entries from JSON
        
    Returns:
        str: Formatted LaTeX for experience section
    """
    if isinstance(experience, list) and experience:
        exp_latex = "\\section{Experience}\n\\resumeSubHeadingListStart\n"
        
        for job in experience:
            company = escape_latex_special_chars(job.get('company', ''))
            title = escape_latex_special_chars(job.get('title', ''))
            location = escape_latex_special_chars(job.get('location', ''))
            dates = escape_latex_special_chars(job.get('dates', ''))
            
            # Handle None values (although escape_latex_special_chars should handle this now)
            company = "" if company is None else company
            title = "" if title is None else title
            location = "" if location is None else location
            dates = "" if dates is None else dates
            
            exp_latex += f"""\\resumeSubheading
{{{title}}}{{{dates}}}
{{{company}}}{{{location}}}
\\resumeItemListStart
"""
            
            # Add bullet points for job details
            details = job.get('details', [])
            if isinstance(details, list) and details:
                for detail in details:
                    detail_text = escape_latex_special_chars(detail)
                    exp_latex += f"\\resumeItem{{{detail_text}}}\n"
            
            exp_latex += "\\resumeItemListEnd\n"
        
        exp_latex += "\\resumeSubHeadingListEnd\n"
        return exp_latex
    
    # Default return if format is unexpected or empty
    return "\\section{Experience}\n\\resumeSubHeadingListStart\n\\resumeSubHeadingListEnd\n"

def format_skills(skills):
    """
    Format skills section for LaTeX.
    
    Args:
        skills (dict or list): Skills information from JSON
        
    Returns:
        str: Formatted LaTeX for skills section
    """
    skills_latex = "\\section{Technical Skills}\n\\begin{itemize}[leftmargin=0pt, itemindent=0pt, labelwidth=0pt, labelsep=0pt, align=left, label={}]%\n\\small{\\item{\n"
    
    # Handle skills as a dictionary with categories (new format)
    if isinstance(skills, dict):
        formatted_skills = []
        
        # Special handling for "Technical Skills" with nested subcategories
        if "Technical Skills" in skills:
            tech_skills = skills["Technical Skills"]
            
            # Case 1: Technical Skills is a dictionary with subcategories
            if isinstance(tech_skills, dict):
                subcategory_parts = []
                
                # Process each subcategory
                for subcategory, subcategory_skills in tech_skills.items():
                    if isinstance(subcategory_skills, list) and subcategory_skills:
                        subcategory_text = escape_latex_special_chars(subcategory)
                        skills_text = ", ".join([escape_latex_special_chars(skill) for skill in subcategory_skills])
                        subcategory_parts.append(f"\\textbf{{{subcategory_text}}}: {skills_text}")
                
                # Add the formatted subcategories directly (without "Technical Skills:" prefix)
                formatted_skills.extend(subcategory_parts)
            
            # Case 2: Technical Skills is an array of skills
            elif isinstance(tech_skills, list) and tech_skills:
                skills_text = ", ".join([escape_latex_special_chars(skill) for skill in tech_skills])
                formatted_skills.append(f"\\textbf{{Technical Skills}}: {skills_text}")
            
            # Remove "Technical Skills" so we don't process it again
            skills_copy = dict(skills)
            del skills_copy["Technical Skills"]
        else:
            skills_copy = skills
        
        # Process each category and its skills
        for category, skill_list in skills_copy.items():
            # Skip if this is "Technical Skills" which we already handled
            if category == "Technical Skills":
                continue
                
            # Format with the category in bold
            category_text = escape_latex_special_chars(category)
            
            # Handle nested structure where skill_list is another dictionary
            if isinstance(skill_list, dict):
                # Create a formatted string for each subcategory
                subcategory_parts = []
                for subcategory, subcategory_skills in skill_list.items():
                    if isinstance(subcategory_skills, list) and subcategory_skills:
                        subcategory_text = escape_latex_special_chars(subcategory)
                        skills_text = ", ".join([escape_latex_special_chars(skill) for skill in subcategory_skills])
                        subcategory_parts.append(f"\\textbf{{{subcategory_text}}}: {skills_text}")
                
                # Join all subcategories with line breaks
                if subcategory_parts:
                    formatted_skills.append(f"\\textbf{{{category_text}}}: " + " \\\\\n".join(subcategory_parts))
            # Handle both list and string values for skills
            elif isinstance(skill_list, list) and skill_list:
                skills_text = ", ".join([escape_latex_special_chars(skill) for skill in skill_list])
                formatted_skills.append(f"\\textbf{{{category_text}}}: {skills_text}")
            else:
                # If it's a string, use it directly
                skills_text = escape_latex_special_chars(str(skill_list))
                formatted_skills.append(f"\\textbf{{{category_text}}}: {skills_text}")
        
        # Join categories with line breaks
        skills_text = " \\\\\n".join(formatted_skills)
        skills_latex += skills_text
    
    # Handle skills as a flat list (legacy format)
    elif isinstance(skills, list) and skills:
        # Make only the category part (before the colon) bold
        formatted_skills = []
        for skill in skills:
            # Check if the skill contains a colon
            if ":" in skill:
                # Split at the first colon
                parts = skill.split(":", 1)
                category = parts[0].strip()
                details = parts[1].strip()
                
                # Format with only the category in bold
                formatted_skill = f"\\textbf{{{escape_latex_special_chars(category)}}}: {escape_latex_special_chars(details)}"
            else:
                # If no colon, just escape the whole skill
                formatted_skill = escape_latex_special_chars(skill)
                
            formatted_skills.append(formatted_skill)
        
        # Join skills with proper LaTeX line breaks
        skills_text = " \\\\\n".join(formatted_skills)
        skills_latex += skills_text
    
    skills_latex += "\n}}\n\\end{itemize}\n"
    return skills_latex

def format_projects(projects):
    """
    Format projects section for LaTeX.
    
    Args:
        projects (list): List of project entries from JSON
        
    Returns:
        str: Formatted LaTeX for projects section
    """
    if isinstance(projects, list) and projects:
        proj_latex = "\\section{Projects}\n\\resumeSubHeadingListStart\n"
        
        for project in projects:
            # Get project name from either 'name' or 'title' field
            project_name = project.get('name', project.get('title', ''))
            project_name = escape_latex_special_chars(project_name)
            
            # Handle technologies as either a string or an array, check technologies_used first
            technologies = project.get('technologies_used', project.get('technologies', ''))
            if technologies is None:
                technologies_formatted = ""
            elif isinstance(technologies, list):
                # Join the technologies list with commas without square brackets
                technologies_formatted = ', '.join([escape_latex_special_chars(tech) for tech in technologies])
            else:
                # Use the technologies string as-is
                technologies_formatted = escape_latex_special_chars(technologies)
            
            # Make sure technologies aren't too long - if they are, we'll break them to a new line
            # Use empty second parameter for dates to avoid text being cut off
            if technologies_formatted and len(technologies_formatted) > 40:  # Threshold for reasonable length
                proj_latex += f"""\\resumeProjectHeading
{{\\textbf{{{project_name}}}}}{{}}
\\resumeItemListStart
\\resumeItem{{\\emph{{Technologies:}} {technologies_formatted}}}
"""
            elif technologies_formatted:
                # Short technology list can be included in the heading 
                proj_latex += f"""\\resumeProjectHeading
{{\\textbf{{{project_name}}} $|$ \\emph{{{technologies_formatted}}}}}{{}}
\\resumeItemListStart
"""
            else:
                # No technologies provided
                proj_latex += f"""\\resumeProjectHeading
{{\\textbf{{{project_name}}}}}{{}}
\\resumeItemListStart
"""
            
            # Add bullet points for project details - check both 'details' and 'description' fields
            details = project.get('details', [])
            
            # Also check for 'description' field and convert to list if it's a string
            description = project.get('description', '')
            if description and not details:
                if isinstance(description, str):
                    details = [description]
                elif isinstance(description, list):
                    details = description
            
            if isinstance(details, list) and details:
                for detail in details:
                    detail_text = escape_latex_special_chars(detail)
                    proj_latex += f"\\resumeItem{{{detail_text}}}\n"
            
            proj_latex += "\\resumeItemListEnd\n"
        
        proj_latex += "\\resumeSubHeadingListEnd\n"
        return proj_latex
    
    # Default return if format is unexpected or empty
    return "\\section{Projects}\n\\resumeSubHeadingListStart\n\\resumeSubHeadingListEnd\n"

#------------------------------------------------------------------------------
# Template Processing Functions 
#------------------------------------------------------------------------------

def populate_template(template, resume_data):
    """
    Replace content in template with resume data from JSON.
    
    Args:
        template (str): LaTeX template content
        resume_data (dict): Resume data parsed from JSON
        
    Returns:
        str: Populated LaTeX template with resume data
    """
    # Create a copy of the template for manipulation
    populated_template = template
    
    # Format the sections first
    sections = {
        'personal_info': format_personal_info(resume_data.get('personal_info', '')),
        'education': format_education(resume_data.get('education', '')),
        'experience': format_experience(resume_data.get('experience', [])),
        'projects': format_projects(resume_data.get('projects', [])),
        'skills': format_skills(resume_data.get('skills', []))
    }
    
    # Replace each section pattern with formatted content
    for section_name, pattern in SECTION_PATTERNS.items():
        # Use a function for replacement to avoid escape sequence issues
        populated_template = re.sub(
            pattern, 
            lambda m: sections[section_name], 
            populated_template, 
            flags=re.DOTALL
        )
    
    # Remove any duplicate sections or unwanted content
    populated_template = re.sub(
        r'%---+\s*\\resumeSubheading.*?(?=\\section|\s*\\end{document})', 
        '', 
        populated_template, 
        flags=re.DOTALL
    )
    
    return populated_template

#------------------------------------------------------------------------------
# Command Line Interface Functions
#------------------------------------------------------------------------------

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Convert JSON resume to LaTeX format and optionally compile to PDF')
    
    # JSON to LaTeX conversion arguments
    parser.add_argument('--json', default=DEFAULT_JSON_PATH, help='Path to JSON resume file')
    parser.add_argument('--template', default=DEFAULT_TEMPLATE_PATH, help='Path to LaTeX template file')
    parser.add_argument('--output', default=DEFAULT_OUTPUT_PATH, help='Path for output LaTeX file')
    
    # LaTeX compilation arguments
    parser.add_argument('--compile', '-c', action='store_true', help='Compile LaTeX file to PDF after generation')
    parser.add_argument('--compiler', choices=['pdflatex', 'latex', 'xelatex', 'lualatex'], 
                        default='pdflatex', help='LaTeX compiler to use')
    parser.add_argument('--output-dir', '-o', help='Directory to store compilation output files')
    parser.add_argument('--stop-on-error', '-s', action='store_true', 
                        help='Stop compilation on first error')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='Print detailed compilation output')
    parser.add_argument('--open', '-p', action='store_true', 
                        help='Open the PDF after successful compilation')
    parser.add_argument('--cleanup', '-C', action='store_true',
                        help='Clean up auxiliary files after compilation, keeping only the PDF')
                        
    return parser.parse_args()

def main():
    """Main function to orchestrate the resume conversion process."""
    # Parse command line arguments
    args = parse_arguments()
    
    print("Starting resume conversion process...")
    
    # Read and parse input files
    print(f"Reading JSON resume from: {args.json}")
    resume_data = read_json_resume(args.json)
    
    print(f"Reading LaTeX template from: {args.template}")
    template = read_latex_template(args.template)
    
    # Process and populate template
    print("Processing resume data and populating template...")
    populated_template = populate_template(template, resume_data)
    
    # Write output
    print(f"Writing output to: {args.output}")
    write_latex_output(populated_template, args.output)
    
    # Compile LaTeX to PDF if requested
    if args.compile:
        compile_success = compile_latex(
            args.output,
            compiler=args.compiler,
            output_dir=args.output_dir,
            continue_on_error=not args.stop_on_error,
            verbose=args.verbose,
            open_pdf=args.open,
            cleanup=args.cleanup
        )
        
        if compile_success:
            print("Resume compilation complete!")
        else:
            print("Resume compilation failed.")
            sys.exit(1)
    else:
        print("Resume conversion complete!")

if __name__ == "__main__":
    main()
