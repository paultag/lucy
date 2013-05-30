from email.mime.text import MIMEText
import smtplib


def send_mail(subject, to, text):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = "lucy@localhost"  # Meh
    msg['To'] = to

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
