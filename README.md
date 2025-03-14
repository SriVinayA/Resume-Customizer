# JSON to LaTeX Resume Converter

A Python-based tool that converts structured JSON resume data into a professionally formatted LaTeX resume.

## Features

- Convert JSON resume data to a LaTeX document
- Support for various resume sections:
  - Personal information with hyperlinked contact details
  - Education history
  - Professional experience
  - Projects
  - Technical skills with categorization
- Clean, maintainable code with proper documentation
- Comprehensive test suite
- Support for different input formats and data structures

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SriVinayA/json-to-latex.git
   cd json-to-latex
   ```

2. Ensure you have Python 3.6+ installed:
   ```bash
   python --version
   ```

3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## Usage

### Basic Usage

```bash
python main.py
```

This will:
1. Read resume data from `resume.json`
2. Read the LaTeX template from `template.tex`
3. Generate a LaTeX resume file at `generated_resume.tex`

### Advanced Usage

You can customize the input and output files:

```bash
python main.py --json path/to/resume.json --template path/to/template.tex --output path/to/output.tex
```

### JSON Format

The resume data in the JSON file should follow this structure:

```json
{
  "personal_info": {
    "name": "Your Name",
    "phone": "123-456-7890",
    "email": "youremail@example.com",
    "linkedin": "linkedin.com/in/yourprofile",
    "github": "github.com/yourusername"
  },
  "education": [
    {
      "institution": "University Name",
      "location": "City, State",
      "degree": "Degree Name",
      "dates": "Start - End"
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "title": "Job Title",
      "location": "City, State",
      "dates": "Start - End",
      "details": [
        "Accomplishment 1",
        "Accomplishment 2"
      ]
    }
  ],
  "skills": {
    "Languages": ["Language 1", "Language 2"],
    "Technologies": ["Tech 1", "Tech 2"]
  },
  "projects": [
    {
      "name": "Project Name",
      "technologies": ["Tech 1", "Tech 2"],
      "details": [
        "Description 1",
        "Description 2"
      ]
    }
  ]
}
```

## Code Structure

The codebase is organized into distinct modules:

- `main.py`: The core functionality including formatting and template population
- `constants.py`: Constants and configurations including regex patterns
- `test_resume_converter.py`: Test suite to validate the functionality

### Key Components

1. **Utility Functions**: Helper functions for text processing and validation
2. **File I/O Functions**: Functions to read JSON and LaTeX files and write output
3. **Formatting Functions**: Functions to convert JSON data into LaTeX code
4. **Template Processing**: Functions to populate the LaTeX template with formatted data

## Testing

Run the test suite to verify functionality:

```bash
python test_resume_converter.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LaTeX template inspired by various resume templates available online
- JSON structure designed to be compatible with modern resume formats 