"""
email_service.py — Robust Email Service supporting HTML emails, real SMTP dispatch
(TLS port 587/25 and SSL port 465), runtime configuration, and Mock Email logging.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import log_email

# Runtime SMTP configuration dictionary
smtp_config = {
    "server": os.getenv("SMTP_SERVER", ""),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "user": os.getenv("SMTP_USER", ""),
    "password": os.getenv("SMTP_PASSWORD", "")
}


def update_smtp_config(server: str, port: int, user: str, password: str):
    """Updates runtime SMTP configuration settings."""
    smtp_config["server"] = server.strip()
    smtp_config["port"] = int(port) if str(port).isdigit() else 587
    smtp_config["user"] = user.strip()
    smtp_config["password"] = password.strip()


def get_smtp_config():
    return {
        "server": smtp_config["server"],
        "port": smtp_config["port"],
        "user": smtp_config["user"],
        "is_configured": bool(smtp_config["server"] and smtp_config["user"] and smtp_config["password"])
    }


def send_email(candidate_id: int, email_type: str, recipient: str, subject: str, body_text: str, body_html: str = None) -> dict:
    """
    Sends an email via SMTP if configured (supporting TLS and SSL),
    otherwise logs into DB in Mock Email Mode.
    """
    server_addr = smtp_config["server"]
    user = smtp_config["user"]
    password = smtp_config["password"]
    port = smtp_config["port"]

    is_smtp = bool(server_addr and user and password)
    delivery_status = "Mock Email Mode (Logged in Database)"
    smtp_error = None

    if is_smtp:
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"HR Recruitment Team <{user}>"
            msg["To"] = recipient
            msg["Subject"] = subject

            msg.attach(MIMEText(body_text, "plain"))
            if body_html:
                msg.attach(MIMEText(body_html, "html"))

            # Port 465 uses SSL, Ports 587 / 25 / 2525 use TLS
            if port == 465:
                with smtplib.SMTP_SSL(server_addr, port, timeout=12) as server:
                    server.login(user, password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(server_addr, port, timeout=12) as server:
                    server.ehlo()
                    try:
                        server.starttls()
                        server.ehlo()
                    except Exception:
                        pass
                    server.login(user, password)
                    server.send_message(msg)

            delivery_status = f"Successfully Sent Live Email to {recipient} via {server_addr}"
            print(f"[Email Service] LIVE EMAIL DELIVERED to {recipient}")
        except Exception as e:
            smtp_error = str(e)
            print(f"[Email Service Error] SMTP failed: {e}")
            delivery_status = f"SMTP Delivery Failed: {smtp_error}"

    # Always log email into SQLite DB for verification
    log_email(candidate_id, email_type, recipient, subject, body_html or body_text)

    return {
        "success": (smtp_error is None),
        "is_smtp": is_smtp,
        "delivery_status": delivery_status,
        "recipient": recipient,
        "subject": subject,
        "body_html": body_html or body_text,
        "smtp_error": smtp_error
    }


def send_interview_link_email(candidate_id: int, candidate_name: str, candidate_email: str, interview_link: str) -> dict:
    """
    Email 1: Initial Interview Invitation with clickable link & HTML button
    """
    subject = "Initial Interview Invitation — AI Recruitment Portal"

    body_text = (
        f"Hello {candidate_name},\n\n"
        "You have been selected for an initial screening interview.\n"
        "Please click the following link to complete your 10-question AI interview:\n\n"
        f"{interview_link}\n\n"
        "Thank you,\n"
        "HR Team"
    )

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .email-card {{ max-width: 600px; background: #ffffff; margin: 0 auto; padding: 30px; border-radius: 8px; border: 1px solid #e1e8ed; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
            .header {{ color: #2563eb; font-size: 20px; font-weight: bold; margin-bottom: 15px; }}
            .btn {{ display: inline-block; background-color: #2563eb; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
            .link-text {{ font-size: 13px; color: #64748b; word-break: break-all; }}
            .footer {{ margin-top: 25px; font-size: 12px; color: #94a3b8; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="email-card">
            <div class="header">Initial Interview Invitation</div>
            <p>Hello <strong>{candidate_name}</strong>,</p>
            <p>We are pleased to inform you that you have been selected for an initial screening interview.</p>
            <p>Please click the button below to start your online 10-question AI interview:</p>
            
            <p><a href="{interview_link}" class="btn" target="_blank">Start Online Interview Test</a></p>
            
            <p class="link-text">Direct Link: <a href="{interview_link}" target="_blank">{interview_link}</a></p>
            
            <div class="footer">
                Thank you,<br>
                <strong>HR Recruitment Team</strong>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(candidate_id, "Initial Interview", candidate_email, subject, body_text, body_html)


def send_final_interview_email(candidate_id: int, candidate_name: str, candidate_email: str) -> dict:
    """
    Email 2: Final Interview Invitation (for PASS candidates)
    """
    subject = "Final Interview Invitation — Congratulations!"

    body_text = (
        f"Congratulations {candidate_name}!\n\n"
        "You have successfully passed the initial interview.\n"
        "We would like to invite you for the final round interview.\n\n"
        "Our HR team will reach out shortly with schedule details.\n\n"
        "Thank you,\n"
        "HR Team"
    )

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .email-card {{ max-width: 600px; background: #ffffff; margin: 0 auto; padding: 30px; border-radius: 8px; border: 1px solid #e1e8ed; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
            .header {{ color: #10b981; font-size: 22px; font-weight: bold; margin-bottom: 15px; }}
            .badge {{ background-color: #d1fae5; color: #047857; padding: 6px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; display: inline-block; margin-bottom: 15px; }}
            .footer {{ margin-top: 25px; font-size: 12px; color: #94a3b8; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="email-card">
            <div class="header">Final Interview Invitation</div>
            <div class="badge">Passed Initial Screening</div>
            <p>Congratulations <strong>{candidate_name}</strong>!</p>
            <p>You have successfully passed the initial AI interview evaluation with flying colors.</p>
            <p>We are delighted to invite you for the final interview round with our senior management team.</p>
            <p>Our team will contact you shortly to coordinate the date and time.</p>
            
            <div class="footer">
                Best regards,<br>
                <strong>HR Recruitment Team</strong>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(candidate_id, "Final Interview", candidate_email, subject, body_text, body_html)
