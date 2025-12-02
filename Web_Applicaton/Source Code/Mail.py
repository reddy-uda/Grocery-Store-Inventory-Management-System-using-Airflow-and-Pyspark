# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib


from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, message, to):
    CLIENT_SECRET_FILE = 'credentials.json'
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['subject'] = subject

    # IMPORTANT: send HTML
    mimeMessage.attach(MIMEText(message, 'html'))

    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    sent_message = service.users().messages().send(
        userId='me', body={'raw': raw_string}
    ).execute()

    print("Email sent:", sent_message)


# send_email("User Details", "hiiiii", "korneliaddanki09@gmail@gmail.com")
#
# otp = random.randint(1000, 10000)
# print(otp)




