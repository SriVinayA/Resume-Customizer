import os
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)
# Set logger level to DEBUG for detailed information
logger.setLevel(logging.DEBUG)

def get_s3_client():
    """
    Create and return an S3 client using AWS credentials from environment variables.
    
    Returns:
        boto3.client: Configured S3 client
    """
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-2")
    s3_bucket = os.getenv("S3_BUCKET_NAME")
    
    logger.debug(f"AWS Config - Region: {aws_region}, Bucket: {s3_bucket}")
    logger.debug(f"AWS Access Key ID exists: {bool(aws_access_key)}")
    logger.debug(f"AWS Secret Access Key exists: {bool(aws_secret_key)}")
    
    if not aws_access_key or not aws_secret_key:
        logger.error("AWS credentials not found in environment variables")
        raise ValueError("AWS credentials not found in environment variables")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        # Test if client works
        s3_client.list_buckets()
        logger.debug("Successfully created S3 client and connected to AWS")
        return s3_client
    except Exception as e:
        logger.error(f"Error creating S3 client: {str(e)}")
        raise

def upload_file_to_s3(file_path, bucket_name, object_name=None, content_type=None):
    """
    Upload a file to an S3 bucket
    
    Args:
        file_path (str): Path to the file to upload
        bucket_name (str): Name of the S3 bucket
        object_name (str, optional): S3 object name. If not specified, file_name is used
        content_type (str, optional): Content type of the file (e.g., 'application/pdf')
        
    Returns:
        str: S3 URL of the uploaded file, or None if upload failed
    """
    # If S3 object_name not specified, use the file name
    if object_name is None:
        object_name = os.path.basename(file_path)

    # Get the S3 client
    s3_client = get_s3_client()
    
    # Prepare extra args for the upload
    extra_args = {}
    if content_type:
        extra_args['ContentType'] = content_type
    
    try:
        logger.debug(f"About to upload file: {file_path} to bucket: {bucket_name}, object: {object_name}")
        s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs=extra_args)
        logger.info(f"File {file_path} uploaded to {bucket_name}/{object_name}")
        
        # Generate S3 URL
        s3_url = f"s3://{bucket_name}/{object_name}"
        logger.debug(f"Generated S3 URL: {s3_url}")
        return s3_url
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        return None

def generate_presigned_url(bucket_name, object_name, expiration=3600, download=False):
    """
    Generate a presigned URL for an S3 object
    
    Args:
        bucket_name (str): Name of the S3 bucket
        object_name (str): Name of the S3 object
        expiration (int, optional): Time in seconds for the URL to remain valid. Default is 1 hour.
        download (bool, optional): If True, the URL will force download, otherwise it will open in browser
        
    Returns:
        str: Presigned URL or None if generation failed
    """
    # Get the region from environment variables
    aws_region = os.getenv("AWS_REGION", "us-east-2")
    
    # Set response headers based on download parameter
    response_headers = {}
    if download:
        filename = os.path.basename(object_name)
        response_headers['ResponseContentDisposition'] = f'attachment; filename="{filename}"'
    
    # Use specific config to ensure regional endpoint and proper signing
    config = boto3.session.Config(
        signature_version='s3v4',
        region_name=aws_region,
        s3={'addressing_style': 'virtual'}  # Use virtual addressing style
    )
    
    try:
        # Create a client with explicit config
        s3_client = boto3.client(
            's3',
            region_name=aws_region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            config=config
        )
        
        logger.debug(f"Generating presigned URL for {bucket_name}/{object_name} in region {aws_region}")
        
        # Generate presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
                **response_headers
            },
            ExpiresIn=expiration
        )
        
        logger.debug(f"Generated presigned URL: {url}")
        return url
    except ClientError as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return None

def download_file_from_s3(bucket_name, object_name, destination_path):
    """
    Download a file from an S3 bucket
    
    Args:
        bucket_name (str): Name of the S3 bucket
        object_name (str): Name of the S3 object
        destination_path (str): Local path to save the downloaded file
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    s3_client = get_s3_client()
    
    try:
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Download the file
        s3_client.download_file(bucket_name, object_name, destination_path)
        logger.info(f"Downloaded {bucket_name}/{object_name} to {destination_path}")
        return True
    except ClientError as e:
        logger.error(f"Error downloading file from S3: {str(e)}")
        return False

def parse_s3_url(s3_url):
    """
    Parse an S3 URL into bucket name and object name
    
    Args:
        s3_url (str): S3 URL in the format 's3://bucket-name/object-name'
        
    Returns:
        tuple: (bucket_name, object_name) or (None, None) if URL is invalid
    """
    if not s3_url or not s3_url.startswith('s3://'):
        return None, None
    
    # Remove 's3://' prefix
    path = s3_url[5:]
    
    # Split into bucket and object path
    parts = path.split('/', 1)
    if len(parts) < 2:
        return parts[0], ''
    
    return parts[0], parts[1] 