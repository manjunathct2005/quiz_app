"""
Builds a polished PDF score report for a completed quiz using reportlab.
Returns raw PDF bytes (also used as the email attachment).
"""
from __future__ import annotations
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

import config


def build_report_pdf(stream: str, subject: str, topic: str, difficulty: str,
                      questions: list[dict], answers: dict[int, str]) -> bytes:
    student_name = config.STUDENT_NAME
    student_email = ", ".join(config.REPORT_EMAILS)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=16 * mm, rightMargin=16 * mm,
        title=f"Quiz Report - {subject} - {topic}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=colors.HexColor("#0f172a"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#1d4ed8"))
    body = ParagraphStyle("BodyX", parent=styles["BodyText"], leading=15)
    small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=9, textColor=colors.grey)
    correct_style = ParagraphStyle("Correct", parent=body, textColor=colors.HexColor("#15803d"))
    wrong_style = ParagraphStyle("Wrong", parent=body, textColor=colors.HexColor("#b91c1c"))

    total = len(questions)
    score = sum(
        1 for i, q in enumerate(questions)
        if answers.get(i) == q["correct_option"]
    )
    pct = round((score / total) * 100, 1) if total else 0

    story = []
    story.append(Paragraph("AI Quiz Teacher — Score Report", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(datetime.now().strftime("Generated on %d %b %Y, %I:%M %p"), small))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#cbd5e1")))
    story.append(Spacer(1, 10))

    meta_table = Table([
        ["Student", student_name or "-", "Email", student_email],
        ["Stream", stream, "Subject", subject],
        ["Topic", topic, "Difficulty", difficulty],
        ["Score", f"{score} / {total}", "Percentage", f"{pct}%"],
    ], colWidths=[28 * mm, 62 * mm, 28 * mm, 62 * mm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#64748b")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#64748b")),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Question-by-question Breakdown", h2))
    story.append(Spacer(1, 6))

    for i, q in enumerate(questions, start=1):
        idx = i - 1
        user_ans = answers.get(idx)
        is_correct = user_ans == q["correct_option"]

        story.append(Paragraph(f"Q{i}. {q['question']}  <font size=8 color='#64748b'>[{q.get('difficulty','')}]</font>", body))
        for opt_key in ("A", "B", "C", "D"):
            label = f"{opt_key}) {q['options'][opt_key]}"
            if opt_key == q["correct_option"] and opt_key == user_ans:
                story.append(Paragraph(f"✔ {label}  — Your answer, Correct", correct_style))
            elif opt_key == q["correct_option"]:
                story.append(Paragraph(f"✔ {label}  — Correct answer", correct_style))
            elif opt_key == user_ans:
                story.append(Paragraph(f"✘ {label}  — Your answer", wrong_style))
            else:
                story.append(Paragraph(label, body))
        if q.get("explanation"):
            story.append(Paragraph(f"<i>Explanation:</i> {q['explanation']}", small))
        story.append(Paragraph(
            "Result: " + ("Correct ✅" if is_correct else ("Not attempted" if user_ans is None else "Incorrect ❌")),
            correct_style if is_correct else wrong_style
        ))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", color=colors.HexColor("#e2e8f0")))
        story.append(Spacer(1, 10))

    doc.build(story)
    return buf.getvalue()
