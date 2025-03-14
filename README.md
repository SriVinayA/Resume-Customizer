# JSON to LaTeX Resume Converter

A Python-based tool that converts structured JSON resume data into a professionally formatted LaTeX resume and optionally compiles it to PDF.

## Features

- Convert JSON resume data to a LaTeX document
- Automatically compile LaTeX to PDF (optional)
- Built-in cleanup of auxiliary LaTeX files
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

4. Ensure you have a LaTeX distribution installed (if you plan to compile to PDF):
   - For macOS: [MacTeX](https://www.tug.org/mactex/)
   - For Windows: [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)
   - For Linux: [TeX Live](https://www.tug.org/texlive/)

## Usage

### Basic Usage

#### Convert JSON to LaTeX only:

```bash
python main.py
```

This will:
1. Read resume data from `resume.json`
2. Read the LaTeX template from `template.tex`
3. Generate a LaTeX resume file at `generated_resume.tex`

#### Convert JSON to LaTeX and compile to PDF:

```bash
python main.py --compile
```

This will perform the above steps and additionally:
4. Compile the LaTeX file to produce `generated_resume.pdf`

#### Convert JSON to LaTeX, compile to PDF, and clean up auxiliary files:

```bash
python main.py --compile --cleanup
```

This removes all the auxiliary files created during LaTeX compilation, keeping only the PDF.

#### Convert, compile, clean up, and open the PDF:

```bash
python main.py --compile --cleanup --open
```

### Advanced Usage

You can customize the input and output files and compilation options:

```bash
python main.py --json path/to/resume.json --template path/to/template.tex --output path/to/output.tex --compile --compiler xelatex --verbose
```

### Available Command-Line Options

#### JSON to LaTeX Conversion:
- `--json`: Path to JSON resume file (default: resume.json)
- `--template`: Path to LaTeX template file (default: template.tex)
- `--output`: Path for output LaTeX file (default: generated_resume.tex)

#### LaTeX Compilation:
- `--compile`, `-c`: Compile LaTeX file to PDF after generation
- `--compiler`: LaTeX compiler to use ('pdflatex', 'latex', 'xelatex', 'lualatex') (default: pdflatex)
- `--output-dir`, `-o`: Directory to store compilation output files
- `--stop-on-error`, `-s`: Stop compilation on first error
- `--verbose`, `-v`: Print detailed compilation output
- `--open`, `-p`: Open the PDF after successful compilation
- `--cleanup`, `-C`: Clean up auxiliary files after compilation, keeping only the PDF

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

- `main.py`: The core functionality including:
  - JSON to LaTeX conversion
  - LaTeX compilation to PDF
  - Template formatting and population
- `constants.py`: Constants and configurations including regex patterns
- `test_resume_converter.py`: Test suite to validate the functionality

### Key Components

1. **Utility Functions**: Helper functions for text processing and validation
2. **File I/O Functions**: Functions to read JSON and LaTeX files and write output
3. **LaTeX Compilation Functions**: Functions to compile LaTeX to PDF and manage auxiliary files
4. **Formatting Functions**: Functions to convert JSON data into LaTeX code
5. **Template Processing**: Functions to populate the LaTeX template with formatted data

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