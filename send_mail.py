import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_email_with_attachments(sender_email, recipients, subject, body_text, bucket_name, file_names, region):
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    ses_client = boto3.client('ses', region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    urls = []
    for file_name in file_names:
        # Generate a pre-signed URL for each S3 object
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=86400  # Link expires in 1 hour
        )
        urls.append(url)

    # Create the email body with the download links
    body_html = f"{body_text}<p>Please download the files from the following links for your analytics report and the session conversation report. Kindly note that the links will expire in 24 hours:</p>"
    for i, url in enumerate(urls):
        body_html += f"<p><a href='{url}'>Download File {i+1}</a></p>"


    # Create the email message
    message = {
        'Subject': {'Data': subject},
        'Body': {'Html': {'Data': body_html}},
    }

    try:
        response = ses_client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': recipients},
            Message=message
        )
        print('Email sent successfully.')
    except ClientError as e:
        print('Error sending email: ', e.response['Error']['Message'])
