import smtplib
from email.mime.text import MIMEText
from project import mysecretstuff

server_name = "smtp.eu.mailgun.org"
port = 587
login_name = mysecretstuff.login_name
login_password = mysecretstuff.login_password


def send_email(who_from, who_to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = who_from
    msg['To'] = who_to

    s = smtplib.SMTP(server_name, port)

    s.login(login_name, login_password)
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

    return
