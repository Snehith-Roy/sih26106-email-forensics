"""
Phase 9 — PDF Forensic Report Generation
Owner: Member 6
"""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


def generate_forensic_report(analysis: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Email Forensic Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    score = analysis["risk_score"]["total_score"]
    elements.append(Paragraph(f"<b>Risk Score:</b> {score}/100", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Score Breakdown", styles["Heading3"]))
    rows = [["Signal", "Points"]] + [
        [k, str(v)] for k, v in analysis["risk_score"]["breakdown"].items()
    ]
    t = Table(rows, colWidths=[300, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Authentication Results", styles["Heading3"]))
    auth = analysis["auth"]
    elements.append(Paragraph(
        f"SPF: {auth['spf_result']} | DKIM: {auth['dkim_result']} "
        f"(independently re-verified: {auth['dkim_independently_verified']}) | "
        f"DMARC: {auth['dmarc_result']}", styles["Normal"]
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Origin Trace", styles["Heading3"]))
    origin = analysis["origin"]
    geo = origin.get("geolocation", {})
    elements.append(Paragraph(
        f"Origin IP: {origin.get('origin_ip')} "
        f"({geo.get('city')}, {geo.get('country')}) — "
        f"trace confidence: {origin.get('trace_confidence')}", styles["Normal"]
    ))
    if origin.get("unverified_self_reported_hops"):
        elements.append(Paragraph(
            "The following relay hops were self-reported by the sending "
            "path and could not be independently verified:", styles["Normal"]
        ))
        for hop in origin["unverified_self_reported_hops"]:
            elements.append(Paragraph(f"— {hop['host']}", styles["Normal"]))

    doc.build(elements)
    return buf.getvalue()
