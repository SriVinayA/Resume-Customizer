# Resume Customizer: AI-Powered Job Application Toolkit

This project is an end-to-end solution for customizing resumes to match job descriptions using AI. It consists of a FastAPI backend and a modern Next.js frontend. The backend leverages DeepSeek AI to parse and tailor resumes, and generates professional PDFs using LaTeX. The frontend provides an elegant, glassmorphism-styled interface for users to upload resumes, input job descriptions, and download customized resumes.

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
├── frontend                   # Next.js frontend
│   ├── src/                   # Source code
│   │   ├── app/               # Next.js app router
│   │   ├── components/        # React components
│   │   ├── services/          # API services
│   │   └── types/             # TypeScript type definitions
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   └── ...
└── README.md                  # Project overview (this file)
```

---

## Features
- **AI Resume Parsing:** Extracts structured data from resumes and job descriptions
- **Resume Customization:** Uses DeepSeek AI to tailor resumes for specific jobs using the STAR method
- **STAR Method Implementation:** All experience and project descriptions follow the Situation, Task, Action, Result format
- **No Summary Section:** Focuses on detailed achievements rather than general summaries
- **PDF Generation:** Converts customized resumes to professional PDFs via LaTeX
- **Modern Frontend:** Elegant glassmorphism-styled UI with modern features
- **Overleaf Integration:** Edit your LaTeX resume directly in Overleaf
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
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Usage
1. Open the frontend in your browser.
2. Upload your resume (PDF) and paste the job description.
3. Click "Customize Resume".
4. View the summary of changes and customized skills.
5. Download the customized PDF or edit in Overleaf.

---

## STAR Method
The application uses the STAR method for all experience and project descriptions:
- **Situation:** Briefly describes the context or challenge
- **Task:** Explains your specific responsibility or goal in that situation
- **Action:** Details the specific steps you took, using action verbs
- **Result:** Quantifies the positive outcome or impact of your actions

This structured approach provides context and clearly demonstrates problem-solving skills and impact to potential employers.

---

## API Overview

- `POST /customize-resume` — Customize a resume for a job description and return PDF
- `GET /download-pdf` — Download generated PDF
- `GET /view-pdf` — View PDF in browser
- `GET /view-latex` — View LaTeX source
- `GET /health` — Health check

Interactive API docs:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Technologies Used
- **Backend**: FastAPI, DeepSeek AI, LaTeX
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS

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
- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
