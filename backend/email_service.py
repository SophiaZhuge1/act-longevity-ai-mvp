from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_report_email(record: dict, pdf_path: Path) -> dict:
    waitlist = record.get("waitlist", {})
    recipient = waitlist.get("email", "").strip()
    if not recipient:
        return {"sent": False, "reason": "No email address supplied."}

    config = smtp_config()
    if not config["host"] or not config["username"] or not config["password"]:
        return {"sent": False, "reason": "Email is not configured. Add SMTP environment variables to send real emails."}

    profile = record.get("profile", {})
    name = profile.get("name") or "there"
    msg = EmailMessage()
    msg["Subject"] = "Your ACT Healthy Longevity taster report"
    msg["From"] = config["from_email"]
    msg["To"] = recipient
    msg.set_content(plain_email_body(name, waitlist.get("join") is True))
    msg.add_alternative(html_email_body(name, waitlist.get("join") is True), subtype="html")

    msg.add_attachment(
        pdf_path.read_bytes(),
        maintype="application",
        subtype="pdf",
        filename=pdf_path.name,
    )

    with smtplib.SMTP(config["host"], config["port"], timeout=20) as smtp:
        if config["use_tls"]:
            smtp.starttls()
        smtp.login(config["username"], config["password"])
        smtp.send_message(msg)

    return {"sent": True, "to": recipient}


def smtp_config() -> dict:
    return {
        "host": os.getenv("SMTP_HOST", ""),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USERNAME", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from_email": os.getenv("SMTP_FROM", os.getenv("SMTP_USERNAME", "ACT <no-reply@actnow.health>")),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() != "false",
    }


def plain_email_body(name: str, joined_waitlist: bool) -> str:
    waitlist_line = (
        "You are also on the interest list for the new ACT AI-powered Healthy Longevity features, and we will let you know when they are ready to try."
        if joined_waitlist
        else "You have not been added to the AI features waitlist."
    )
    return f"""Hi {name},

Thank you for completing the ACT Assess taster.

Your Healthy Longevity report is attached as a PDF. It summarises your priorities for support, prevention opportunities, clinical risks to discuss with your doctor and your five-dimension profile.

{waitlist_line}

This report is for wellness support and is not a diagnosis.

Warm wishes,
The ACT team
"""


def html_email_body(name: str, joined_waitlist: bool) -> str:
    waitlist_line = (
        "You are also on the interest list for the new <b>ACT AI-powered Healthy Longevity</b> features, and we will let you know when they are ready to try."
        if joined_waitlist
        else "You have not been added to the AI features waitlist."
    )
    return f"""
    <div style="font-family: Georgia, serif; color: #17202e; line-height: 1.5;">
      <h1 style="color: #062838;">Your ACT Healthy Longevity report</h1>
      <p>Hi {name},</p>
      <p>Thank you for completing the ACT Assess taster.</p>
      <p>Your Healthy Longevity report is attached as a PDF. It summarises your priorities for support, prevention opportunities, clinical risks to discuss with your doctor and your five-dimension profile.</p>
      <p>{waitlist_line}</p>
      <p style="color: #667085;">This report is for wellness support and is not a diagnosis.</p>
      <p>Warm wishes,<br>The ACT team</p>
    </div>
    """
