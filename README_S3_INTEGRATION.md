# AWS S3 Integration for Resume-Customizer

## Overview

The Resume-Customizer application now stores generated PDFs and JSON files in AWS S3, providing several benefits:

- Scalable storage solution independent of server disk space
- Better availability and durability for files
- Direct access to files without server load
- CDN integration possibility for faster global access

## Implementation Details

### 1. Required AWS Resources

- **S3 Bucket**: A bucket to store generated PDFs and JSON files
- **IAM User**: With programmatic access and appropriate S3 permissions
- **IAM Policy**: Allows PUT, GET, and LIST operations on the bucket

### 2. Environment Configuration

The following environment variables are required in the `.env` file:

```
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-2  # Use the region where your bucket is located
S3_BUCKET_NAME=your-bucket-name
```

### 3. Core Components

The S3 integration consists of several key components:

#### S3 Utility Module (`pdf_generator/s3_utils.py`)

- **`get_s3_client()`**: Creates an authenticated S3 client using AWS credentials
- **`upload_file_to_s3()`**: Uploads files to S3 with proper content types
- **`generate_presigned_url()`**: Generates secure, time-limited URLs for viewing/downloading files
- **`download_file_from_s3()`**: Downloads files from S3 to the local filesystem
- **`parse_s3_url()`**: Parses S3 URLs of the format `s3://bucket-name/object-name`

#### Integration Points

1. **PDF Generation**: In `generate_resume_pdf()`, PDFs are uploaded to S3 after local generation
2. **JSON Storage**: In `save_resume_json()`, JSON files are uploaded to S3
3. **LaTeX Storage**: LaTeX source files are uploaded to S3 to enable Overleaf integration
4. **Viewing Files**: The `/view-pdf/` endpoint supports direct S3 access via presigned URLs
5. **Downloading Files**: The `/download-pdf/` endpoint supports S3 downloads via presigned URLs
6. **LaTeX Access**: The `/view-latex/` endpoint supports fetching LaTeX files from S3

### 4. Important Implementation Notes

- Presigned URLs use the virtual-hosted style addressing (`bucket-name.s3.region.amazonaws.com`)
- S3v4 signature version is used for all S3 operations
- URLs are generated with 1-hour expiration by default
- Files are stored in organized paths:
  - PDFs: `resumes/filename.pdf`
  - LaTeX files: `latex/filename.tex`
  - JSON: `json/filename.json`

### 5. ATS Scoring and S3 Integration

The ATS Compatibility Scoring feature is fully integrated with the S3 storage solution:

- **JSON file storage**: Complete ATS evaluation data (including scores, feedback, and keyword analysis) is stored in the JSON files uploaded to S3.
- **Efficient retrieval**: When viewing a resume from S3, the ATS scores are fetched with the resume data.
- **Data persistence**: Both original and optimized resume scores are preserved even if the server is restarted.
- **Score and resume linking**: ATS evaluation data is linked to the specific resume version, ensuring accurate before/after comparisons.

This integration allows users to access their ATS evaluation data at any time by loading the PDF through the application, even after browser sessions have ended.

### 6. LaTeX File Storage

LaTeX source files are stored in S3 to enable seamless integration with Overleaf:

- **Storage Location**: LaTeX files are stored in the `latex/` folder in the S3 bucket
- **Naming Convention**: LaTeX files use the same base filename as the PDF (e.g., `resume_name.pdf` → `resume_name.tex`)
- **Content Type**: LaTeX files are stored with the `text/plain` content type
- **Access Control**: Same permissions as PDF and JSON files
- **Retrieval**: The `/view-latex/` endpoint handles fetching the LaTeX file from S3 when given the PDF's S3 URL

This enables users to:
1. Generate a customized resume
2. View and download the PDF
3. Edit the LaTeX source directly in Overleaf for fine-tuning
4. Download the updated PDF from Overleaf

## Troubleshooting

Common issues and solutions:

1. **SignatureDoesNotMatch errors**: These typically occur when there's a mismatch between the endpoint used for URL generation and the one expected by S3. Our implementation ensures correct regional endpoints are used.

2. **Access Denied errors**: Check IAM permissions to ensure the IAM user has appropriate permissions on the bucket.

3. **Missing files**: Verify that both the S3_BUCKET_NAME and AWS_REGION environment variables are correctly set.

4. **Missing ATS data**: If ATS scores aren't displayed when viewing a resume from S3, ensure the corresponding JSON file exists in the `json/` folder of your S3 bucket.

5. **LaTeX file not found errors**: When trying to edit in Overleaf, check that:
   - The LaTeX file was properly uploaded to the `latex/` folder in S3
   - The filename in S3 matches the pattern expected (should be the same base name as the PDF)
   - Your IAM user has permission to access the `latex/` folder in S3

## Maintenance

Regular tasks to maintain the S3 integration:

1. **Credential rotation**: Periodically rotate AWS credentials for security
2. **Bucket cleanup**: Implement a lifecycle policy to delete old files if needed
3. **Monitoring**: Monitor S3 usage and costs

## Future Enhancements

Potential future improvements:

1. **CloudFront integration**: Add CDN for faster global access
2. **Direct uploads**: Allow direct browser-to-S3 uploads for large files
3. **Server-side encryption**: Implement encryption for sensitive files
4. **Versioning**: Enable bucket versioning to maintain file history
5. **ATS history tracking**: Store historical ATS evaluations to track improvement over time
