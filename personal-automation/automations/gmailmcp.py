from fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import functools
import os
import json
import base64
from email.message import EmailMessage
from automations.gmail_categorization import categorize_gmail_emails
from automations.gmail_types import GmailThreadHeader


mcp = FastMCP('Gmail')


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


@mcp.tool()
async def read_thread(threadId: str):
    service = get_gmail_service()
    results = service.users().threads().get(userId='me', id=threadId, format='full').execute()
    return results


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
async def process_inbox():
    threads = await get_inbox_threads()
    clf_response = await categorize_gmail_emails(threads)
    for email, classification in zip(clf_response.emails, clf_response.classifications):
        if classification.classification == "draft_reply":
            print(f"Drafting reply for thread {email.id}: {email.snippet}")
            await write_draft_reply(email.id, email.to_email, email.subject, email.content)
        elif classification.classification == "archive":
            print(f"Archiving thread {email.id}: {email.snippet}")
            await archive_thead(email.id)
    return True