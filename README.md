# Resume Customizer: AI-Powered Job Application Toolkit

This project is an end-to-end solution for customizing resumes to match job descriptions using AI. It consists of a FastAPI backend and a simple web frontend. The backend leverages DeepSeek AI to parse and tailor resumes, and generates professional PDFs using LaTeX. The frontend provides an easy-to-use web interface for users to upload resumes, input job descriptions, and download customized resumes.

---

## Project Structure

```
.
├── backend
│   ├── main.py                # FastAPI backend API
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (API keys)
│   ├── pdf_generator/         # PDF/LaTeX generation utilities
│   └── ...
├── frontend
│   ├── index.html             # Main web UI
│   ├── static/
│   │   ├── css/style.css      # Styles
│   │   └── js/app.js          # Frontend logic
│   ├── serve.py               # Simple static file server
│   └── ...
└── README.md                  # Project overview (this file)
```

---

## Features
- **AI Resume Parsing:** Extracts structured data from resumes and job descriptions
- **Resume Customization:** Uses DeepSeek AI to tailor resumes for specific jobs
- **PDF Generation:** Converts customized resumes to professional PDFs via LaTeX
- **Web Frontend:** Simple UI for uploading resumes, entering job descriptions, and downloading results
- **API Endpoints:** RESTful endpoints for all major operations

---

## Setup Instructions

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file with your DeepSeek API key:
   ```
   DEEPSEEK_API_KEY=your-api-key-here
   ```
4. Install LaTeX (required for PDF generation):
   - **macOS:** `brew install --cask mactex`
   - **Ubuntu/Debian:** `sudo apt-get install texlive-full`
   - **Windows:** Download and install [MiKTeX](https://miktex.org/download)

5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at: http://localhost:8000

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Start the frontend server:
   ```bash
   python serve.py
   ```
   Or, use any static HTTP server (e.g., `python -m http.server 3000`).

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Usage
1. Open the frontend in your browser.
2. Upload your resume (PDF) and paste the job description.
3. Click "Customize Resume".
4. View the summary of changes and download the customized PDF.

---

## API Overview

- `POST /process_application` — Analyze a job description and resume, return tailored content
- `POST /customize_resume` — Customize a resume for a job description and return PDF
- `GET /download_pdf` — Download generated PDF
- `GET /view_pdf` — View PDF in browser
- `GET /view_latex` — View LaTeX source
- `GET /health` — Health check

Interactive API docs:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Contributing
Pull requests and issues are welcome! Please review the backend and frontend READMEs for more detailed component-specific information.

---

## License
This project is for educational and demonstration purposes. See individual files for license details.

---

## Credits
- [FastAPI](https://fastapi.tiangolo.com/)
- [DeepSeek AI](https://deepseek.com/)
- [LaTeX](https://www.latex-project.org/)
