#!/usr/bin/env python3
"""Send AI daily digest email via 163 SMTP."""
import json
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "ai-daily-email.json"


def load_config():
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    if cfg["sender_password"] == "YOUR_SMTP_AUTH_CODE_HERE":
        print("ERROR: Please set your 163 SMTP auth code in ai-daily-email.json")
        sys.exit(1)
    return cfg


def send_email(subject: str, body_html: str, body_text: str = ""):
    cfg = load_config()
    msg = MIMEMultipart("alternative")
    msg["From"] = cfg["sender_email"]
    msg["To"] = cfg["receiver_email"]
    msg["Subject"] = subject

    if body_text:
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    timeout = cfg.get("smtp_timeout", 30)
    if cfg.get("smtp_ssl", True):
        server = smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"], timeout=timeout)
    else:
        server = smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=timeout)
        server.starttls()

    server.login(cfg["sender_email"], cfg["sender_password"])
    server.sendmail(cfg["sender_email"], cfg["receiver_email"], msg.as_string())
    server.quit()
    print(f"Email sent to {cfg['receiver_email']} at {datetime.now()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: send_daily_email.py <subject> [body_file]")
        print("  body_file: path to HTML content file (default: email.html)")
        sys.exit(1)

    subject = sys.argv[1]
    
    # 如果没有指定文件，自动使用 email.html
    if len(sys.argv) >= 3:
        body_file = sys.argv[2]
    else:
        # 自动查找 email.html
        script_dir = Path(__file__).parent.parent
        body_file = script_dir / "email.html"
        if not body_file.exists():
            body_file = script_dir / "index.html"
    
    with open(body_file) as f:
        body_html = f.read()
    send_email(subject, body_html)
