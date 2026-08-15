"""
SMTP email helpers.

Two emails go out during a session:
1. A "task assigned" notification when a quiz is started (teacher-style
   assignment note: subject, topic, difficulty, number of questions).
2. The final PDF score report, attached, once the quiz is completed.

Both always go to config.REPORT_RECIPIENTS (both fixed addresses) --
there's no login and no email entry in the app itself.
"""
from __future__ import annotations
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import config


def _check_smtp_configured():
    if not config.SMTP_APP_PASSWORD or "PASTE_YOUR" in config.SMTP_APP_PASSWORD:
        raise RuntimeError(
            "SMTP_APP_PASSWORD is not set. Open config.py and paste a Gmail App "
            "Password (from https://myaccount.google.com/apppasswords)."
        )


def _send(msg: MIMEMultipart, to_emails: list[str]):
    _check_smtp_configured()
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_APP_PASSWORD)
        server.sendmail(config.SMTP_USER, to_emails, msg.as_string())


def send_task_notification(student_name: str, stream: str,
                            subject: str, topic: str, difficulty: str, n_questions: int):
    to_emails = config.REPORT_RECIPIENTS
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📘 New Quiz Assigned: {subject} — {topic}"
    msg["From"] = config.SMTP_USER
    msg["To"] = ", ".join(to_emails)

    text = f"""Hi {student_name or config.DEFAULT_STUDENT_NAME},

A new test has been set for you by your AI Quiz Teacher:

Stream      : {stream}
Subject     : {subject}
Topic       : {topic}
Difficulty  : {difficulty}
Questions   : {n_questions}

Head back to the quiz portal to attempt it now. Good luck!

- AI Quiz Teacher
"""
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;background:#0f172a;padding:24px;border-radius:12px;color:#e2e8f0;">
      <h2 style="color:#38bdf8;margin-top:0;">📘 New Quiz Assigned</h2>
      <p>Hi {student_name or config.DEFAULT_STUDENT_NAME},</p>
      <p>A new test has been set for you by your <b>AI Quiz Teacher</b>:</p>
      <table style="width:100%;border-collapse:collapse;margin:16px 0;">
        <tr><td style="padding:8px;color:#94a3b8;">Stream</td><td style="padding:8px;font-weight:600;">{stream}</td></tr>
        <tr><td style="padding:8px;color:#94a3b8;">Subject</td><td style="padding:8px;font-weight:600;">{subject}</td></tr>
        <tr><td style="padding:8px;color:#94a3b8;">Topic</td><td style="padding:8px;font-weight:600;">{topic}</td></tr>
        <tr><td style="padding:8px;color:#94a3b8;">Difficulty</td><td style="padding:8px;font-weight:600;">{difficulty}</td></tr>
        <tr><td style="padding:8px;color:#94a3b8;">Questions</td><td style="padding:8px;font-weight:600;">{n_questions}</td></tr>
      </table>
      <p>Head back to the quiz portal to attempt it now. Good luck! 🍀</p>
      <p style="color:#64748b;font-size:12px;">— AI Quiz Teacher</p>
    </div>
    """
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    _send(msg, to_emails)


def send_report_email(student_name: str, subject: str, topic: str,
                       score: int, total: int, pdf_bytes: bytes, pdf_filename: str):
    to_emails = config.REPORT_RECIPIENTS
    msg = MIMEMultipart("mixed")
    msg["Subject"] = f"📄 Quiz Report: {subject} — {topic} ({score}/{total})"
    msg["From"] = config.SMTP_USER
    msg["To"] = ", ".join(to_emails)

    body = MIMEMultipart("alternative")
    text = f"""Hi {student_name or config.DEFAULT_STUDENT_NAME},

Here is your quiz report for {subject} — {topic}.
Score: {score} / {total}

The detailed PDF report is attached, with a question-by-question breakdown,
correct answers and explanations.

- AI Quiz Teacher
"""
    html = f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;background:#0f172a;padding:24px;border-radius:12px;color:#e2e8f0;">
      <h2 style="color:#22c55e;margin-top:0;">📄 Your Quiz Report is Ready</h2>
      <p>Hi {student_name or config.DEFAULT_STUDENT_NAME},</p>
      <p><b>{subject} — {topic}</b></p>
      <p style="font-size:22px;font-weight:700;color:#38bdf8;">Score: {score} / {total}</p>
      <p>The detailed PDF report is attached with a question-by-question
      breakdown, correct answers and explanations.</p>
      <p style="color:#64748b;font-size:12px;">— AI Quiz Teacher</p>
    </div>
    """
    body.attach(MIMEText(text, "plain"))
    body.attach(MIMEText(html, "html"))
    msg.attach(body)

    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename=pdf_filename)
    msg.attach(attachment)

    _send(msg, to_emails)
