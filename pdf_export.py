import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def find_arabic_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def export_papers_pdf(papers, output_path, language="Arabic"):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    font_path = find_arabic_font()
    if font_path:
        pdfmetrics.registerFont(TTFont("CustomFont", font_path))
        font_name = "CustomFont"
    else:
        font_name = "Helvetica"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=18,
        leading=22,
        spaceAfter=16,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=10,
        leading=14,
        alignment=1,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=13,
        leading=18,
        spaceBefore=12,
        spaceAfter=6,
    )

    story = []
    story.append(Paragraph("تقرير الأبحاث العلمية" if language == "Arabic" else "Academic Research Report", title_style))
    story.append(Spacer(1, 10))

    for index, paper in enumerate(papers, start=1):
        title = paper.get("title", "")
        authors = paper.get("authors", "")
        year = paper.get("year", "")
        source_name = paper.get("source_name", "")
        source_url = paper.get("source_url", "")
        keywords = paper.get("keywords", "") or "-"
        summary = paper.get("summary", "") or paper.get("abstract", "") or "-"
        notes = paper.get("notes", "") or "-"

        if language == "Arabic":
            story.append(Paragraph(f"{index}. {title}", heading_style))
            story.append(Paragraph(f"المؤلفون: {authors}", body_style))
            story.append(Paragraph(f"السنة: {year}", body_style))
            story.append(Paragraph(f"المصدر: {source_name}", body_style))
            story.append(Paragraph(f"الرابط: {source_url}", body_style))
            story.append(Paragraph(f"الكلمات المفتاحية: {keywords}", body_style))
            story.append(Paragraph(f"الملخص: {summary}", body_style))
            story.append(Paragraph(f"الملاحظات: {notes}", body_style))
        else:
            story.append(Paragraph(f"{index}. {title}", heading_style))
            story.append(Paragraph(f"Authors: {authors}", body_style))
            story.append(Paragraph(f"Year: {year}", body_style))
            story.append(Paragraph(f"Source: {source_name}", body_style))
            story.append(Paragraph(f"Link: {source_url}", body_style))
            story.append(Paragraph(f"Keywords: {keywords}", body_style))
            story.append(Paragraph(f"Summary: {summary}", body_style))
            story.append(Paragraph(f"Notes: {notes}", body_style))

        story.append(Spacer(1, 10))

    doc.build(story)
    return output_path
