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
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# from oauth2client.client import Credentials
from google.oauth2.credentials import Credentials
from jinja2 import Template
from quickstart import SCOPES


def send_message_with_attachment(receiver, sub, content, content_html):
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

    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)
        mime_message = EmailMessage()

        # headers
        mime_message['To'] = receiver
        mime_message['From'] = 'Python Test <pythontestarjun@gmail.com>'  # From E-Mail ID
        mime_message['Subject'] = sub

        # text content
        mime_message.set_content(content)

        # Add the html version.  This converts the message into a multipart/alternative
        # container, with the original text message as the first part and the new html
        # message as the second part.
        mime_message.add_alternative(content_html, subtype='html')

        # attachment
        attachment_filename = 'Arjun\'s Resume & Cover Letter.pdf'

        # guessing the MIME type
        type_subtype, _ = mimetypes.guess_type(attachment_filename)
        maintype, subtype = type_subtype.split('/')

        with open(attachment_filename, 'rb') as fp:
            attachment_data = fp.read()
        mime_message.add_attachment(attachment_data, maintype, subtype,
                                    filename=attachment_filename)  # Filename issue fix => added filename argument

        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message


if __name__ == '__main__':

    # Mailing List as Dictionary
    mailing_list = {
        "Arjun Jayesh": "<9997arjun@gmail.com>",
    }

    # Subject Line
    sub = "Resume - Arjun Jayesh"

    # Alternative Plain Text Content
    content = """Hi %s, 
    
    """

    # HTML Content
    content_html = f"""\
<html>
  <body>
    <p>{{name}}</p>
    <p>
        Click here to visit <a href="http://www.google.co.in">Google</a> Website.
    </p>
  </body>
</html>
"""
    for key, value in mailing_list.items():
        print("Sent to %s" % key)

        tm = Template("Hello {{name}}") # Initialize Jinja object tm
        content_html = tm.render(name=name) # Render Jinja to content_html

        send_message_with_attachment(value, sub, content %key, content_html)