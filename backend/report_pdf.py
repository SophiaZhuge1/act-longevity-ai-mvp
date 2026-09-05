from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


REPORT_DIR = Path(__file__).resolve().parent / "data" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

PUBLIC_SCORE_KEYS = [
    ("staying_healthy", "Staying Healthy"),
    ("independence", "Independence"),
    ("wellbeing", "Wellbeing"),
    ("accommodation", "Quality of Accommodation"),
    ("financial_wellbeing", "Financial Wellbeing"),
]


def create_pdf_report(record: dict) -> Path:
    profile = record.get("profile", {})
    user_id = record.get("user_id", "report")
    name = profile.get("name") or "ACT member"
    path = REPORT_DIR / f"{user_id}-act-healthy-longevity-report.pdf"

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=46,
        leftMargin=46,
        topMargin=44,
        bottomMargin=44,
        title=f"ACT Healthy Longevity Report - {name}",
    )
    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#062838")
    styles["Heading2"].textColor = colors.HexColor("#062838")
    styles["BodyText"].fontSize = 10.5
    styles["BodyText"].leading = 14

    story = [
        Paragraph("ACT Healthy Longevity Taster Report", styles["Title"]),
        Paragraph(f"Prepared for {name}", styles["Heading2"]),
        Paragraph(
            "This is a wellness summary, not a diagnosis. It is designed to help you notice priorities for support, prevention opportunities and points to discuss with a doctor or trusted professional.",
            styles["BodyText"],
        ),
        Spacer(1, 14),
        Paragraph("Healthy Longevity Profile", styles["Heading2"]),
        score_table(record.get("scores", {})),
        Spacer(1, 12),
        Paragraph("Plain-English Summary", styles["Heading2"]),
        Paragraph(escape_text(record.get("persona", "")), styles["BodyText"]),
    ]

    add_section(story, styles, "Priorities for Support", record.get("support_priorities", []))
    add_section(story, styles, "Prevention Opportunities", record.get("prevention_opportunities", []))
    add_section(story, styles, "Clinical Risks to Discuss", record.get("clinical_risks", []))
    add_section(story, styles, "Suggested Local and Home Support", record.get("recommendations", []))

    story += [
        Spacer(1, 10),
        Paragraph("What happens next?", styles["Heading2"]),
        Paragraph(
            "You have been added to the ACT Healthy Longevity interest list if you opted in. We will contact you when the AI-powered support features are ready to try.",
            styles["BodyText"],
        ),
    ]
    doc.build(story)
    return path


def score_table(scores: dict) -> Table:
    rows = [["Dimension", "Score"]]
    rows.extend([[label, f"{scores.get(key, 0)}/100"] for key, label in PUBLIC_SCORE_KEYS])
    table = Table(rows, colWidths=[330, 90])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7f5f6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#062838")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d8ddd5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfbf6")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def add_section(story: list, styles, title: str, items: list[dict]) -> None:
    story.append(Spacer(1, 12))
    story.append(Paragraph(title, styles["Heading2"]))
    if not items:
        story.append(Paragraph("No major items were identified from the current answers.", styles["BodyText"]))
        return
    for item in items:
        heading = escape_text(item.get("title", "Item"))
        body = escape_text(item.get("body", ""))
        story.append(Paragraph(f"<b>{heading}</b>", styles["BodyText"]))
        for line in wrap(body, 100) or [""]:
            story.append(Paragraph(line, styles["BodyText"]))
        story.append(Spacer(1, 6))


def escape_text(value: str) -> str:
    return (value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
