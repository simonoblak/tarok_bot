import smtplib
import ssl
import base64
# import requests


def send_email(email_message=""):
    sender_email, receiver_emails, base64_password = [line.rstrip('\n') for line in open("resources/email_config.txt", 'r', encoding='utf8')]
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    password = str(base64.b64decode(base64_password), "utf-8")

    message = """TAROK EJGA
    Subject: TAROK bot napaka
    
    Go fix: """ + email_message

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        for receiver_email in receiver_emails.split(","):
            server.sendmail(sender_email, receiver_email, message.encode("utf-8"))





