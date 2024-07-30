import email
from email.header import decode_header
import email.utils
import imaplib
import json
import os
import html2text
import time
from django.utils.dateparse import parse_datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from bs4 import BeautifulSoup  # For extracting text from HTML content
from cosmoft import settings
from maills.models import Email, File, Message
from asgiref.sync import sync_to_async
import uuid

detach_dir = './maills/resources'
        

class EmailWorker:
    EMAIL_TYPE_SERVER = {
        'gmail.com': 'imap.gmail.com',
        'yandex.ru': 'imap.yandex.ru',
        'mail.ru': 'imap.mail.ru',
    }

    def __init__(self, email: str, email_type: str):
        self.email = email
        self.email_type = email_type
        self.status = True

    async def fetch_emails(self, websocket: AsyncWebsocketConsumer):
        if self.email_type not in self.EMAIL_TYPE_SERVER:
            raise ValueError(f"Unsupported email type: {self.email_type}")

        mail_obj = await sync_to_async(Email.objects.get)(email=self.email, type=self.email_type)
        if not mail_obj:
            raise Exception('Email not found')

        # Get the date of the last email stored in the database for this email address
        last_email_date = await self.get_last_email_date()

        mail = imaplib.IMAP4_SSL(self.EMAIL_TYPE_SERVER[self.email_type])
        try:
            print("Connecting to email server...", self.email.strip(), mail_obj.password.strip())
            mail.login(self.email.strip(), mail_obj.password.strip())
            mail.select('inbox')

            # Fetch emails since the last saved date
            date_query = f'SINCE "{last_email_date.strftime("%d-%b-%Y")}"' if last_email_date else 'ALL'
            result, data = mail.search(None, date_query)
            email_ids = data[0].split()
            total_emails = len(email_ids)
            print("Consuming emails: ", total_emails)

            for index, email_id in enumerate(email_ids):
                if not self.status:
                    break

                result, message_data = mail.fetch(email_id, '(RFC822)')
                raw_email = message_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Parse necessary data from the email
                subject = self.decode_mime_words(msg['subject'])
                body = self.get_email_body(msg)
                date_sent = email.utils.parsedate_to_datetime(msg['date'])
                message_id = msg.get('Message-ID')

                # Check if this message already exists in the database
                if await self.is_duplicate_message(message_id):
                    print(f"Skipping duplicate message: {subject} on {date_sent}")
                    continue

                # Save the message to the database
                message_obj = await self.save_message(subject, body, date_sent, message_id)

                print(f"Message {subject} on {date_sent} saved to database")

                # Handle attachments
                attachments = await self.save_attachments(msg, message_obj)
              

                # Update email message records
                await sync_to_async(mail_obj.messages.add)(message_obj)
                
                # Send progress update via WebSocket
                progress = (index + 1) / total_emails * 100
                await websocket.send(text_data=json.dumps({
                    'type': 'progress_update',
                    'progress': progress,
                    'message': {
                        "email_type": mail_obj.type,
                        'heading': subject,
                        'date_sent': date_sent.isoformat(),
                        'content': body[:50] + '...',
                        'date_got': date_sent.isoformat(),
                        'attachments': [{'id': att.id, 'file_name': att.name} for att in attachments]
                    }
                }))
        finally:
            mail.logout()

    async def get_last_email_date(self):
        # Get the most recent email date for this email address from the database
        last_email = await sync_to_async(Message.objects.filter(emails__email=self.email).order_by('-date_sent').first)()
        return last_email.date_sent if last_email else None

    async def is_duplicate_message(self, message_id: str) -> bool:
        # Check if the message already exists in the database
        exist =  await sync_to_async(Message.objects.filter)(message_id=message_id)
        return await sync_to_async(exist.exists)()

    async def save_message(self, subject, body, date_sent, message_id) -> Message:
        # Save the message in the database
        return await sync_to_async(Message.objects.create)(
            heading=subject,
            content=body,
            date_got=date_sent,
            date_sent=date_sent,
            message_id=message_id
        )

    def stop_fetching(self):
        self.status = False

    def decode_mime_words(self, s):
        # Decode MIME-encoded words in headers
        decoded_string = ''
        for word, charset in decode_header(s):
            if isinstance(word, bytes):
                word = word.decode(charset or 'utf-8')
            decoded_string += word
        return decoded_string

    def get_email_body(self, msg):
        # Get the body of the email
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                # Skip attachments and non-text parts
                if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is not None:
                    continue

                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)

                if content_type == 'text/plain':
                    # Handle plain text content
                    body += payload.decode('utf-8', errors='ignore').strip()
                elif content_type == 'text/html':
                    # Handle HTML content
                    soup = BeautifulSoup(payload, 'html.parser')
                    body += soup.get_text().strip()

        else:
            # Handle single part emails
            payload = msg.get_payload(decode=True)
            content_type = msg.get_content_type()

            if content_type == 'text/plain':
                body = payload.decode('utf-8', errors='ignore')
            elif content_type == 'text/html':
                soup = BeautifulSoup(payload, 'html.parser')
                body = soup.get_text()

        return body

    async def save_attachments(self, msg, message_obj: Message) -> list[File]:
        res = []
        # Save attachments
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue
            file_name = part.get_filename()
            att_path = self.save_attachment(part)
            if(not file_name or not att_path or not message_obj):
                print('Skipping attachment:', file_name)
                continue

            file_obj, created = await sync_to_async(File.objects.get_or_create)(name=file_name, path=att_path)
            if created:
                await sync_to_async(message_obj.attachments.add)(file_obj)
            res.append(file_obj)
        return res

    def save_attachment(self, part):
        # Save a single attachment
        filename = part.get_filename()
        if filename:
            # Ensure the directory exists
            resources_dir = os.path.join(settings.BASE_DIR, 'maills', 'resources')
            os.makedirs(resources_dir, exist_ok=True)
            filename = uuid.uuid4().hex
            print('Saving attachment:', filename)
            att_path = os.path.join(resources_dir, filename)
            if not os.path.isfile(att_path):
                try:
                    with open(att_path, 'wb') as fp:
                        fp.write(part.get_payload(decode=True))
                    print('Downloaded file:', filename)
                    return att_path
                except:
                    print('Error saving attachment:', filename)
                    return None
        return None

        