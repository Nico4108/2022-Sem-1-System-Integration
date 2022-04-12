#   https://realpython.com/python-send-email/

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

def send_email(receiver_email, random_auth_code):
    sender_email = "nicspieg0208@gmail.com"
    #receiver_email = "nicspieg0208@gmail.com"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Verification Code"
    message["From"] = sender_email
    message["To"] = receiver_email

    #random_auth_code = random.randint(100000, 999999)

    # Create the plain-text and HTML version of your message
    text = f"""\
    Hi, your code is: {random_auth_code}
    """

    html = f"""\
    <html>
    <body>
        <p>
        Hi, your code is: {random_auth_code}
        </p>
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        try:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        except Exception as ex:
            print(ex)
