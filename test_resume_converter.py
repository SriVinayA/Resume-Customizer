import unittest
import os
import json
import re
from main import (
    escape_latex_special_chars, 
    format_personal_info, 
    format_education,
    format_skills,
    format_projects,
    format_experience,
    populate_template,
    is_email,
    is_linkedin,
    is_github,
    is_phone,
    ensure_url_protocol
)

class TestResumeConverter(unittest.TestCase):
    """Test suite for the JSON to LaTeX resume converter."""
    
    def test_escape_latex_special_chars(self):
        """Test LaTeX character escaping."""
        # Test various special characters
        self.assertEqual(escape_latex_special_chars('$100 & 10%'), r'\$100 \& 10\%')
        self.assertEqual(escape_latex_special_chars('_{test}'), r'\_\{test\}')
        
        # The actual output when escaping '\test'
        actual_output = escape_latex_special_chars('\\test')
        self.assertTrue('textbackslash' in actual_output)
        self.assertTrue('test' in actual_output)
        
    def test_is_email(self):
        """Test email detection."""
        self.assertTrue(is_email('test@example.com'))
        self.assertTrue(is_email('user.name@domain.co.uk'))
        self.assertFalse(is_email('not-an-email'))
        self.assertFalse(is_email('missing@domain'))
        
    def test_is_linkedin(self):
        """Test LinkedIn profile detection."""
        self.assertTrue(is_linkedin('linkedin.com/in/username'))
        self.assertTrue(is_linkedin('https://linkedin.com/in/username'))
        self.assertFalse(is_linkedin('github.com/username'))
        
    def test_is_github(self):
        """Test GitHub profile detection."""
        self.assertTrue(is_github('github.com/username'))
        self.assertTrue(is_github('https://github.com/username'))
        self.assertFalse(is_github('linkedin.com/in/username'))
        
    def test_is_phone(self):
        """Test phone number detection."""
        self.assertTrue(is_phone('123-456-7890'))
        self.assertTrue(is_phone('(123) 456-7890'))
        self.assertFalse(is_phone('123-456'))  # Too few digits
        
    def test_ensure_url_protocol(self):
        """Test URL protocol addition."""
        self.assertEqual(ensure_url_protocol('github.com/user'), 'https://github.com/user')
        self.assertEqual(ensure_url_protocol('https://github.com/user'), 'https://github.com/user')
        self.assertEqual(ensure_url_protocol('http://example.com'), 'http://example.com')
        
    def test_format_personal_info_dict(self):
        """Test personal info formatting with dictionary input."""
        test_info = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '123-456-7890',
            'linkedin': 'linkedin.com/in/johndoe',
            'github': 'github.com/johndoe'
        }
        result = format_personal_info(test_info)
        # Check that name is included
        self.assertIn('John Doe', result)
        # Check that links are formatted correctly
        self.assertIn(r'\href{mailto:john@example.com}{\underline{john@example.com}}', result)
        self.assertIn(r'\href{https://linkedin.com/in/johndoe}{\underline{linkedin.com/in/johndoe}}', result)
        
    def test_format_education_list(self):
        """Test education formatting with list input."""
        test_education = [
            {
                'institution': 'Test University',
                'location': 'Test City, ST',
                'degree': 'Bachelor of Science in Computer Science',
                'dates': 'Aug 2015 - May 2019'
            }
        ]
        result = format_education(test_education)
        # Check that education details are included
        self.assertIn('Test University', result)
        self.assertIn('Test City, ST', result)
        self.assertIn('Bachelor of Science in Computer Science', result)
        
    def test_format_skills_dict(self):
        """Test skills formatting with dictionary input."""
        test_skills = {
            'Languages': ['Python', 'JavaScript', 'Java'],
            'Frameworks': ['React', 'Django', 'Spring']
        }
        result = format_skills(test_skills)
        # Check that skills are properly categorized
        self.assertIn(r'\textbf{Languages}', result)
        self.assertIn('Python, JavaScript, Java', result)
        self.assertIn(r'\textbf{Frameworks}', result)
        self.assertIn('React, Django, Spring', result)
        
    def test_populate_template(self):
        """Test template population with dummy data."""
        # Create a minimal test template
        test_template = """
\\documentclass{article}
\\begin{document}

\\begin{center}
\\textbf{\\Huge \\scshape Template Name} \\\\ \\vspace{1pt}
\\small template@example.com
\\end{center}

\\section{Education}
\\resumeSubHeadingListStart
\\resumeSubHeadingListEnd

\\end{document}
"""
        # Create test resume data
        test_data = {
            'personal_info': {'name': 'Test Name', 'email': 'test@example.com'},
            'education': [
                {
                    'institution': 'Test School',
                    'location': 'Test Location',
                    'degree': 'Test Degree',
                    'dates': 'Test Dates'
                }
            ]
        }
        
        result = populate_template(test_template, test_data)
        # Check that template was populated
        self.assertIn('Test Name', result)
        self.assertIn('test@example.com', result)
        self.assertIn('Test School', result)
        self.assertIn('Test Degree', result)
        self.assertNotIn('Template Name', result)

if __name__ == '__main__':
    unittest.main() 