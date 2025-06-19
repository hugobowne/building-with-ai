from fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import functools
import os
import json
import base64
from email.message import EmailMessage
from automations.gmail_categorization import categorize_gmail_emails, draft_reply
from automations.gmail_types import GmailThreadHeader, GmailThread


mcp = FastMCP('Gmail')

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
]

def get_oauth_info() -> dict:
    oauth_file = os.path.join(os.environ["HOME"], '.gmail-mcp/gcp-oauth.keys.json')
    with open(oauth_file, 'r') as f:
        return json.load(f)

def get_cred_info() -> dict:
    cred_file = os.path.join(os.environ["HOME"], '.gmail-mcp/credentials.json')
    with open(cred_file, 'r') as f:
        return json.load(f)
    
def get_creds() -> Credentials:
    oauth_info = get_oauth_info()
    cred_info = get_cred_info()
    info = {
        **cred_info, **oauth_info['installed']
    }
    return Credentials.from_authorized_user_info(info)

@mcp.tool()
async def login():
    oauth_file = os.path.join(os.environ["HOME"], '.gmail-mcp/gcp-oauth.keys.json')
    
    flow = InstalledAppFlow.from_client_secrets_file(oauth_file, SCOPES)
    creds = flow.run_local_server(port=0)
    
    cred_info = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    
    cred_file = os.path.join(os.environ["HOME"], '.gmail-mcp/credentials.json')
    with open(cred_file, 'w') as f:
        json.dump(cred_info, f)
    
    return "Login successful - credentials saved"

@functools.lru_cache(maxsize=1)
def get_gmail_service():
    creds = get_creds()
    return build('gmail', 'v1', credentials=creds)


# WARNING: this api has pagination we are not using, so you might not get all the results!
@mcp.tool()
async def get_inbox_threads() -> list[GmailThreadHeader]:
    service = get_gmail_service()
    results = service.users().threads().list(userId='me', q="in:inbox").execute()
    return [GmailThreadHeader(**thread) for thread in results.get('threads', [])]


def _extract_text_from_payload(payload):
    """Extract plain text content from Gmail message payload."""
    if payload.get('body', {}).get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    if payload.get('parts'):
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part.get('parts'):
                text = _extract_text_from_payload(part)
                if text:
                    return text
    
    return ""

def _get_header_value(headers, name):
    """Get header value by name from Gmail message headers."""
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return ""

def _map_thread_to_gmail_thread(thread_data) -> GmailThread:
    """Map Gmail API thread response to GmailThread model."""
    messages = thread_data.get('messages', [])
    if not messages:
        raise ValueError("Thread has no messages")
    
    # Get the last message for reply information
    last_message = messages[-1]
    headers = last_message.get('payload', {}).get('headers', [])
    
    # Extract reply information from the last message
    reply_email = _get_header_value(headers, 'From')
    reply_subject = _get_header_value(headers, 'Subject')
    reply_content = _extract_text_from_payload(last_message.get('payload', {}))
    
    return GmailThread(
        id=thread_data['id'],
        snippet=thread_data.get('snippet', ''),
        reply_email=reply_email,
        reply_subject=reply_subject,
        reply_content=reply_content
    )

@mcp.tool()
async def read_thread(threadId: str) -> GmailThread:
    service = get_gmail_service()
    results = service.users().threads().get(userId='me', id=threadId, format='full').execute()
    return _map_thread_to_gmail_thread(results)


@mcp.tool()
async def archive_thead(threadId: str):
    service = get_gmail_service()
    service.users().threads().modify(userId='me', id=threadId, body={'removeLabelIds': ['INBOX']}).execute()
    return True


@mcp.tool()
async def write_draft_reply(threadId: str, to_email: str, subject: str, content: str):
    service = get_gmail_service()
    message = EmailMessage()
    message.set_content(content)

    message['To'] = to_email
    message['From'] = 'me@skylarbpayne.com'
    message['Subject'] = subject
    
    create_message = {
        'message': {
            'threadId': threadId,
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
        }
    }
    service.users().drafts().create(userId='me', body=create_message).execute()
    return True
        

@mcp.tool()
async def process_inbox(max_emails: int | None = None):
    # Note: the `.fn` is due to how the @mcp.tool() decorator works.
    threads = await get_inbox_threads.fn()
    max_emails = max_emails or len(threads)
    clf_response = categorize_gmail_emails(threads[:max_emails])
    for email, classification in zip(clf_response.emails, clf_response.classifications):
        if classification.classification == "draft_reply":
            print(f"Drafting reply for thread {email.id}: {email.snippet}")
            thread = await read_thread.fn(email.id)
            reply = await draft_reply(thread.reply_content)
            await write_draft_reply.fn(email.id, thread.reply_email, thread.reply_subject, reply.content)
        elif classification.classification == "archive":
            print(f"Archiving thread {email.id}: {email.snippet}")
            await archive_thead.fn(email.id)
    return True