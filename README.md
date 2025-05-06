# Resume Customizer: AI-Powered Job Application Toolkit

This project is an end-to-end solution for customizing resumes to match job descriptions using AI. It consists of a FastAPI backend and a modern Next.js frontend. The backend leverages OpenAI to parse and tailor resumes, and generates professional PDFs using LaTeX. The frontend provides an elegant, glassmorphism-styled interface for users to upload resumes, input job descriptions, and download customized resumes.

---

## Project Structure

```
.
├── backend
│   ├── main.py                # FastAPI backend API
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (API keys)
│   ├── pdf_generator/         # PDF/LaTeX generation utilities
│   │   ├── s3_utils.py        # AWS S3 integration utilities
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
└── README_S3_INTEGRATION.md   # AWS S3 integration documentation
```

---

## Features
- **AI Resume Parsing:** Extracts structured data from resumes and job descriptions
- **Resume Customization:** Uses OpenAI to tailor resumes for specific jobs using the STAR method
- **STAR Method Implementation:** All experience and project descriptions follow the Situation, Task, Action, Result format
- **No Summary Section:** Focuses on detailed achievements rather than general summaries
- **PDF Generation:** Converts customized resumes to professional PDFs via LaTeX
- **AWS S3 Integration:** Stores and serves PDFs from scalable cloud storage
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
3. Set up your `.env` file with your OpenAI API key and AWS credentials:
   ```
   OPENAI_API_KEY=your-api-key-here
   
   # AWS S3 Configuration (optional but recommended)
   AWS_ACCESS_KEY_ID=your-access-key-here
   AWS_SECRET_ACCESS_KEY=your-secret-key-here
   AWS_REGION=us-east-2  # Or your preferred region
   S3_BUCKET_NAME=your-bucket-name
   ```
4. Install LaTeX (required for PDF generation):
   - **macOS:** `brew install --cask mactex`
   - **Ubuntu/Debian:** `sudo apt-get install texlive-full`
   - **Windows:** Download and install [MiKTeX](https://miktex.org/download)

5. (Optional) Set up AWS S3 bucket for PDF storage:
   - Create an S3 bucket in your AWS account
   - Ensure the IAM user has appropriate permissions (see README_S3_INTEGRATION.md)

6. Start the backend server:
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
6. If AWS S3 is configured, PDFs will be stored in the cloud for improved scalability and availability.

---

## STAR Method
The application uses the STAR method for all experience and project descriptions:
- **Situation:** Briefly describes the context or challenge
- **Task:** Explains your specific responsibility or goal in that situation
- **Action:** Details the specific steps you took, using action verbs
- **Result:** Quantifies the positive outcome or impact of your actions

This structured approach provides context and clearly demonstrates problem-solving skills and impact to potential employers.

---

## AWS S3 Integration

The application can be configured to store generated PDFs and JSON files in AWS S3, providing:
- Scalable storage independent of server disk space
- Better availability and durability for files
- Faster access via direct S3 presigned URLs

See [README_S3_INTEGRATION.md](./README_S3_INTEGRATION.md) for detailed setup instructions.

---

## API Overview

- `POST /customize-resume` — Customize a resume for a job description and return PDF
- `GET /download-pdf` — Download generated PDF (local or S3)
- `GET /view-pdf` — View PDF in browser (local or S3)
- `GET /view-latex` — View LaTeX source
- `GET /health` — Health check

Interactive API docs:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Technologies Used
- **Backend**: FastAPI, OpenAI, LaTeX, AWS S3
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
- [OpenAI](https://openai.com/)
- [LaTeX](https://www.latex-project.org/)
- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [AWS S3](https://aws.amazon.com/s3/)
