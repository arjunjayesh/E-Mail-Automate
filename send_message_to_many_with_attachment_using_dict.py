from __future__ import print_function
from fileinput import filename

import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
import mimetypes
import os
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# from oauth2client.client import Credentials
from google.oauth2.credentials import Credentials

from quickstart import SCOPES


def send_message_with_attachment(receiver, sub, content):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # creds, _ = google.auth.default()

    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)
        mime_message = EmailMessage()

        # headers
        mime_message['To'] = receiver
        mime_message['From'] = 'Test <from@email.com>' #From E-Mail ID
        mime_message['Subject'] = sub

        # text
        mime_message.set_content(content)

        # attachment
        attachment_filename = 'Test File.pdf'
        # guessing the MIME type
        type_subtype, _ = mimetypes.guess_type(attachment_filename)
        maintype, subtype = type_subtype.split('/')

        with open(attachment_filename, 'rb') as fp:
            attachment_data = fp.read()
        mime_message.add_attachment(attachment_data, maintype, subtype,
                                    filename=attachment_filename)  # Filename issue fix => Just added filename argument

        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message


if __name__ == '__main__':
    mailing_list = {
        "Name": "<name@email.com>",
    } # Mailing List as Dictionary
    sub = "Automated Test E-Mail" # Subject Line
    content = """Hi %s, 
    
This is an Automated Test E-Mail. 
    
Thanks
Name
""" # Formatted Content
    for key,value in mailing_list.items():
        print("Sent to %s"%key)
        send_message_with_attachment(value, sub, content %key)
