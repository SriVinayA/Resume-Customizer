import json
import re
import os
import sys
import argparse
from constants import (
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
    if not isinstance(text, str):
        return text
    
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
        if 'github' in personal_info:
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
                
                if institution.endswith(location):
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
    skills_latex = "\\section{Technical Skills}\n\\begin{itemize}[leftmargin=0.15in, label={}]\n\\small{\\item{\n"
    
    # Handle skills as a dictionary with categories (new format)
    if isinstance(skills, dict):
        formatted_skills = []
        
        # Process each category and its skills
        for category, skill_list in skills.items():
            if isinstance(skill_list, list) and skill_list:
                # Format with the category in bold
                category_text = escape_latex_special_chars(category)
                skills_text = ", ".join([escape_latex_special_chars(skill) for skill in skill_list])
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
            
            # Handle technologies as either a string or an array
            technologies = project.get('technologies', '')
            if isinstance(technologies, list):
                # Join the technologies list with commas without square brackets
                technologies_formatted = ', '.join([escape_latex_special_chars(tech) for tech in technologies])
            else:
                # Use the technologies string as-is
                technologies_formatted = escape_latex_special_chars(technologies)
            
            proj_latex += f"""\\resumeProjectHeading
{{\\textbf{{{project_name}}} $|$ \\emph{{{technologies_formatted}}}}}{{}}
\\resumeItemListStart
"""
            
            # Add bullet points for project details
            details = project.get('details', [])
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
    parser = argparse.ArgumentParser(description='Convert JSON resume to LaTeX format')
    parser.add_argument('--json', default=DEFAULT_JSON_PATH, help='Path to JSON resume file')
    parser.add_argument('--template', default=DEFAULT_TEMPLATE_PATH, help='Path to LaTeX template file')
    parser.add_argument('--output', default=DEFAULT_OUTPUT_PATH, help='Path for output LaTeX file')
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
    
    print("Resume conversion complete!")

if __name__ == "__main__":
    main()
