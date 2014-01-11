from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import exporter

def send_posts(posts, msg_from, msg_to, smtp_address, user, passwd):
    s = smtplib.SMTP_SSL(smtp_address)
    s.login(user, passwd)
    msgs = []
    feed_ids = exporter.get_feed_ids(posts)
    html_pages = exporter.generate_html_pages(posts, 'category', feed_ids)
    for name, page in html_pages.items():
        msg = MIMEMultipart('alternative')
        msg['From'] = msg_from
        msg['To'] = msg_to
        msg['Subject'] = name
        text = ""
        html = page
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        msgs.append(msg)
    for msg in msgs:
        s.sendmail(msg_from, msg_to, msg.as_string())
    s.quit()

    


