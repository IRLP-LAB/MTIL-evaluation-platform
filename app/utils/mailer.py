import os
import smtplib
import ssl
from fastapi import HTTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def account_mail_verifier(subject, body,email_recipient, mail_placholder):
    email_sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")
    try:
        # Create a MIMEMultipart message
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = email_sender
        msg["To"] = email_recipient

        # Replace placeholders in the HTML template
        body = body.replace("{username}", mail_placholder["name"])
        body = body.replace("{varification-link}", mail_placholder["link"])

        # Create the HTML content and attach it to the email
        html_content = MIMEText(body, "html")
        msg.attach(html_content)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_recipient, msg.as_string())
        print("Email sent!")

    except Exception as err:
        raise HTTPException(status_code=421, detail="Mail Error") from err
    
    