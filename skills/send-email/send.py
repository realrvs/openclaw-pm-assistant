import smtplib
import os
import sys
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path.home() / ".openclaw/workspace/skills/send-email/.env")
except ImportError:
    pass

def send_email(to, subject, body, smtp_server=None, smtp_port=None, smtp_user=None, smtp_password=None, from_email=None):
    smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.yandex.ru")
    smtp_port = int(smtp_port or os.getenv("SMTP_PORT", 465))
    smtp_user = smtp_user or os.getenv("SMTP_USER")
    smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
    from_email = from_email or os.getenv("FROM_EMAIL", smtp_user)
    
    if not smtp_user or not smtp_password:
        print("❌ Ошибка: SMTP_USER и SMTP_PASSWORD должны быть заданы в .env файле")
        sys.exit(1)
    
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Письмо успешно отправлено на {to}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Отправка email через SMTP")
    parser.add_argument("--to", required=True, help="Email получателя")
    parser.add_argument("--subject", required=True, help="Тема письма")
    parser.add_argument("--body", required=True, help="Текст письма")
    args = parser.parse_args()
    
    send_email(args.to, args.subject, args.body)
