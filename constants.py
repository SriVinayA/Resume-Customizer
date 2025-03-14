"""
Constants and configuration values for the JSON to LaTeX resume converter.
"""

# File paths and defaults
DEFAULT_JSON_PATH = 'resume.json'
DEFAULT_TEMPLATE_PATH = 'template.tex'
DEFAULT_OUTPUT_PATH = 'generated_resume.tex'

# LaTeX special characters and their replacements
LATEX_SPECIAL_CHARS = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}'
}

# Regex patterns for section matching in LaTeX templates
SECTION_PATTERNS = {
    'personal_info': r'\\begin{center}\s*\\textbf{\\Huge \\scshape.+?\\end{center}',
    'education': r'\\section{Education}\s*\\resumeSubHeadingListStart.*?\\resumeSubHeadingListEnd',
    'experience': r'\\section{Experience}\s*\\resumeSubHeadingListStart.*?\\resumeSubHeadingListEnd',
    'projects': r'\\section{Projects}\s*\\resumeSubHeadingListStart.*?\\resumeSubHeadingListEnd',
    'skills': r'\\section{Technical Skills}\s*\\begin{itemize}.*?\\end{itemize}'
}

# Regex patterns for parsing education entries from string
EDUCATION_PATTERNS = {
    'institution_split': r'(University|Institute|College|Aug \d{4})',
    'location': r'([A-Za-z]+,\s*[A-Z]{2}|[A-Za-z]+,\s*[A-Za-z]+)',
    'degree': r'((?:Master|Bachelor|PhD|Doctor)[^,\n]*(?:Science|Arts|Engineering|Computer)[^,\n]*)',
    'dates': r'(Aug \d{4} – May \d{4})'
}

# Patterns for identifying link types in contact information
EMAIL_PATTERN = r'@.*\.'
LINKEDIN_PATTERN = 'linkedin.com'
GITHUB_PATTERN = 'github.com'
PHONE_MIN_DIGITS = 7 