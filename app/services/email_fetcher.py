from imap_tools import MailBox, AND
from email.message import EmailMessage
import os
from datetime import datetime, UTC
from app.core.config import settings
import re


def extract_original_sender(from_header: str, text: str) -> str:
    """Extract original sender from forwarded emails."""
    # First try to find "From:" in the email body
    if text:
        # Look for "From:" followed by name and email pattern
        match = re.search(r'From:\s*"([^"]+)"\s*<[^>]+>', text)
        if match:
            return match.group(1)  # Return the display name
        
        # Alternative pattern for forwarded emails
        match = re.search(r'From:\s*"([^"]+)"\s*<[^>]+>', from_header)
        if match:
            return match.group(1)
    
    # Fallback to the from_header if no match found
    match = re.search(r'"([^"]+)"', from_header)
    if match:
        return match.group(1)
    return from_header


def fetch_new_emails():
    mailbox = MailBox("imap.gmail.com")
    mailbox.login(settings.gmail_username, settings.gmail_password)

    new_count = 0
    for msg in mailbox.fetch(AND(seen=False)):
        email_obj = EmailMessage()
        original_sender = extract_original_sender(msg.from_, msg.text or msg.html or "")
        email_obj["From"] = original_sender
        email_obj["To"] = "update@bjorkupdates.com"
        email_obj["Subject"] = msg.subject
        email_obj["Date"] = msg.date_str
        email_obj.set_content(msg.text or msg.html or "")

        safe_sender = original_sender.replace("@", "_").replace(">", "").replace("<", "")
        timestamp = datetime.now(UTC).isoformat()
        fname = f"{timestamp}_{safe_sender}.eml"

        path = os.path.join(settings.email_dir, fname)
        with open(path, "wb") as f:
            f.write(bytes(email_obj))

        mailbox.flag(msg.uid, "\\Seen", True)
        new_count += 1

    mailbox.logout()
    return new_count