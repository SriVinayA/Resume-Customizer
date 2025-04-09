# Resume Customizer UI

This is a simple web interface for interacting with the Resume Customizer API. It allows users to upload a resume, enter a job description, and get a customized resume with PDF output.

## Features

- Upload resume in PDF format
- Enter job description
- View customized resume details
- Download generated PDF
- View raw JSON response

## How to Run

### 1. Start the Backend API

First, make sure the FastAPI backend is running:

```bash
cd backend
uvicorn main:app --reload
```

The API should be available at http://localhost:8000.

### 2. Start the Frontend Server

You can start the frontend server using the provided script:

```bash
cd frontend
python serve.py
```

This will start a local web server on port 3000 and open a browser automatically.

Alternatively, you can run any HTTP server in the frontend directory:

```bash
cd frontend
python -m http.server 3000
```

Then visit http://localhost:3000 in your browser.

## Usage

1. Upload your resume (PDF)
2. Enter a job description
3. Click "Customize Resume"
4. View the customized resume details
5. Download the generated PDF by clicking "Download PDF"

## Test Data

You can find a sample resume in the `samples` directory to test the application. 