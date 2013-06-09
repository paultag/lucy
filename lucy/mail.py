from email.mime.text import MIMEText
from email.parser import Parser
from jinja2 import Template
from io import StringIO
import smtplib
import os


TEMPLATE_ROOT = os.path.join(os.path.dirname(__file__), "templates/mails")


def send_mail(template, **context):
    path = Template(open("%s/%s" % (TEMPLATE_ROOT, template)).read())
    buf = StringIO(path.render(**context))
    email = Parser().parse(buf)
    s = smtplib.SMTP('localhost')
    s.send_message(email)
    s.quit()
