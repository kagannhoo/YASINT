import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..config import get_settings
from ..database import SessionLocal
from ..models.analysis import Analysis, Finding


def generate_pdf(analysis_id: str) -> str:
    settings = get_settings()
    reports_dir = Path(settings.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = reports_dir / f"{analysis_id}.pdf"

    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == UUID(analysis_id)).first()
        if not analysis:
            raise ValueError("Analysis not found")

        findings = (
            db.query(Finding)
            .filter(Finding.analysis_id == UUID(analysis_id))
            .all()
        )

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            textColor=colors.HexColor("#00d4aa"),
            fontSize=22,
            spaceAfter=20,
        )
        heading_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#e8eaf0"),
            fontSize=14,
            spaceBefore=12,
            spaceAfter=8,
        )

        story = []
        story.append(Paragraph("YASINT Analiz Raporu", title_style))
        story.append(
            Paragraph(
                f"Hedef: {analysis.target_name or 'Belirtilmemiş'}<br/>"
                f"Tarih: {analysis.created_at.strftime('%Y-%m-%d %H:%M')}<br/>"
                f"Güven Skoru: {analysis.confidence_score:.0%}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.5 * cm))

        llm_finding = next((f for f in findings if f.module == "llm"), None)
        if llm_finding:
            story.append(Paragraph("Profil Özeti", heading_style))
            try:
                profile = json.loads(llm_finding.value)
                story.append(
                    Paragraph(
                        profile.get("identity_summary", ""),
                        styles["Normal"],
                    )
                )
            except json.JSONDecodeError:
                story.append(Paragraph(llm_finding.value, styles["Normal"]))
            story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("Bulgular", heading_style))
        table_data = [["Modül", "Kategori", "Anahtar", "Değer", "Güven"]]
        for f in findings:
            if f.module == "llm":
                continue
            conf = f"{f.confidence:.0%}" if f.confidence else "—"
            val = f.value[:80] + "..." if len(f.value) > 80 else f.value
            table_data.append([f.module, f.category, f.key, val, conf])

        if len(table_data) > 1:
            t = Table(table_data, colWidths=[2.5 * cm, 2.5 * cm, 3 * cm, 6 * cm, 2 * cm])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1d24")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#00d4aa")),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
                    ]
                )
            )
            story.append(t)

        story.append(Spacer(1, 1 * cm))
        story.append(
            Paragraph(
                f"Rapor oluşturulma: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                styles["Italic"],
            )
        )

        doc.build(story)
        return str(pdf_path)
    finally:
        db.close()
