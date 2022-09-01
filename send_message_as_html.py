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

Hope you are doing fine. 
 
I am reaching out to you in regards to career opportunities at UST and found your contact from LinkedIn. I think my skills could bring in a lot of value to your organization. 
  
My roots are from a computer science background and I am currently looking for opportunities that would help me transform my career by transitioning into the development. 
 
I have been preparing for this transition by taking up internships and upskilling. Currently, I am working on Django and would be working on flask the end of this month.

Do visit my GitHub page to see what I am working on right now. Further, you can also find me on LinkedIn to learn more comprehensively about my experience. Please find my resume and cover letter attached. 

LinkedIn: https://www.linkedin.com/in/arjunjayesh
GitHub: https://github.com/arjunjayesh
E-Mail: 9997arjun@gmail.com
Phone: +91 70129 36126
 
Hoping to get in touch with you soon. 
 
Kind Regards,
Arjun Jayesh
"""


    for key, value in mailing_list.items():
        print("Sent to %s" % key)

        # HTML Content
        content_html = f"""\
        <html>
          <body>
            <p>Hello {key.split(' ')[0]},</p>
            <p>Hope you are doing fine.</p>

            <p>I am reaching out to you in regard to career opportunities at UST and found your contact from <a href="https://www.linkedin.com/in/arjunjayesh">LinkedIn</a>. I think my skills could bring in a lot of value to your organization.</p>
            
            <p>My roots are from a computer science background and I am currently looking for opportunities that would help me transform my career by transitioning into the development.</p>
            
            <p>I have been preparing for this transition by taking up internships and upskilling. Currently, I am working on Django and would be working on flask the end of this month.</p>
            
            <p>Do visit my <a href="https://github.com/arjunjayesh">GitHub</a> page to see what I am working on right now. Further, you can also find me on <a href="https://www.linkedin.com/in/arjunjayesh">LinkedIn</a> to learn more comprehensively about my experience.</p>
            
            <p>Please find my resume and cover letter attached for your reference.</p>
            
            <p>Hoping to get in touch with you soon.</p>

            <p>
                Regards<br>Arjun Jayesh<br><br>
                <a href="https://www.linkedin.com/in/arjunjayesh">LinkedIn</a> | <a href="https://github.com/arjunjayesh">GitHub</a>
                <br>
                <a href="mailto:9997arjun@gmail.com">E-Mail</a> | <a href="https://wa.me/+917012936126">+91 70129 36126</a>
            </p>
          </body>
        </html>
        """
        # name = key
        # tm = Template("{{name}}")  # Initialize Jinja object tm
        # content_html = tm.render(name=name)  # Render Jinja to content_html

        send_message_with_attachment(value, sub, content % key, content_html)
