
import os
import re
import bleach
import base64
import django
import trafilatura as tf

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from django.db.utils import IntegrityError

from ollama_summarise import summarise_text

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from read.models import Text
from read.utils import bleach_text
from read.parsers import convert_date

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate and return the Gmail API service."""
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials, authenticate the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def clean_sender(x):
    return re.sub(r"\s\<[A-Za-z0-9_@+.]+\>", "", x)

def decode_message(payload):
    """Decode the message payload from base64."""
    decoded_bytes = base64.urlsafe_b64decode(payload.encode('UTF-8'))
    return decoded_bytes.decode('UTF-8')

def parse_emails(service):
    """Fetch the latest email from the user's Gmail inbox."""
    # Get the list of messages
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("No messages found.")
        return
    
    # Get the details of the latest message
    for m in messages:
        msg = service.users().messages().get(userId='me', id=m['id']).execute()
        # Decode the email content
        headers = msg['payload']['headers']
        date = convert_date(next(header['value'] for header in headers if header['name'] == 'Date'))
        sender = clean_sender(next(header['value'] for header in headers if header['name'] == 'From'))
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        
        parts = msg.get('payload', {}).get('parts', [])
        body = ""
        for part in parts:
            if part.get('mimeType') == 'text/html':
                body = body + bleach.clean(decode_message(part['body']['data']), tags = {'a', 'i', 'img', 'b', 'p'}, strip=True)
            # elif part.get('mimeType') == 'text/plain':
                # pass
                # body = body + "<p>" + decode_message(part['body']['data']) + "</p>"
        
        print(f"Subject: {subject}")
        
        t = Text(link = m["id"], publication_date = date, author = sender, title = subject, 
                 summary = summarise_text(body), content = body, source = sender)
        try:
            t.save()
        except IntegrityError:
            pass


if __name__ == '__main__':
    service = authenticate_gmail()
    parse_emails(service)
