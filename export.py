from pathlib import Path
from datetime import datetime
import re

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    ListFlowable,
    ListItem, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


EXPORT_DIR = Path(__file__).parent / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def format_value(value):
    if isinstance(value, dict):
        return ", ".join(
            f"{key}: {format_value(item)}"
            for key, item in value.items()
        )

    if isinstance(value, list):
        if not value:
            return "Не определено"

        return "; ".join(
            format_value(item) for item in value
        )

    return str(value)


def create_filename(title, extension):
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    safe_title = safe_title.replace(" ", "_")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe_title}_{timestamp}.{extension}"

def export_to_docx(specification):
    EXPORT_DIR.mkdir(exist_ok=True)

    document = Document()

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = title.add_run("ТЕХНИЧЕСКОЕ ЗАДАНИЕ")
    run.bold = True
    run.font.size = Pt(24)

    document.add_paragraph("\n\n\n")

    project_title = document.add_paragraph()
    project_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    project_name = specification["overview"]["title"]

    run = project_title.add_run(project_name)
    run.bold = True
    run.font.size = Pt(18)

    document.add_paragraph("\n\n")

    date_paragraph = document.add_paragraph()
    date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    date_paragraph.add_run(
        f"Дата создания: {datetime.now().strftime('%d.%m.%Y')}"
    )
    version_paragraph = document.add_paragraph()
    version_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    version_paragraph.add_run("Версия документа: 1.0")

    document.add_page_break()

    document.add_heading(
        "Техническое задание",
        level=0,
    )
    overview = specification["overview"]

    document.add_heading("1.Общая информация", level=1)

    for key, value in overview.items():
        document.add_paragraph(f"{key}: {value}")

    document.add_heading("2.Функциональные требования", level=1)
    functional_requirements = specification["functional_requirements"]
    table = document.add_table(rows=1, cols=4)

    headers = [
        "ID",
        "Название функции",
        "Описание",
        "Приоритет"
    ]

    for cell,header in zip(table.rows[0].cells, headers):
        cell.text = header

    for index,item in  enumerate(functional_requirements,start=1):
        row = table.add_row()
        row.cells[0].text = f"FR-{index:03d}"
        row.cells[1].text = str(item["name"])
        row.cells[2].text = str(item["description"])
        row.cells[3].text = str(item["priority"])


    document.add_heading("3. Технические требования", level=1)

    technical_requirements = specification["technical_requirements"]

    if isinstance(technical_requirements, dict):

        for key, value in technical_requirements.items():
            document.add_paragraph(
                f"{key}: {format_value(value)}"
            )

    elif isinstance(technical_requirements, list):

        for item in technical_requirements:
            document.add_paragraph(
                format_value(item),
                style="List Bullet"
            )

    else:
        document.add_paragraph(format_value(technical_requirements))

    document.add_heading("4.Критерии приемки", level=1)
    for item in specification["acceptance_criterion"]:
        document.add_heading(item["requirement"], level=2)
        document.add_paragraph(item["expected_result"])

    document.add_heading("5.План разработки", level=1)
    for step in specification["develop_plan"]:
        document.add_paragraph(step, style="List Number")


    document.styles["Normal"].font.name = "Arial"
    document.styles["Normal"].font.size = Pt(11)

    filename = create_filename(
        overview["title"],
        "docx"
    )

    path = EXPORT_DIR / filename
    document.save(path)

    print(f"\nDOCX успешно сохранён: {path}")

    return path

def register_pdf_font():
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    bold_font_path = Path("C:/Windows/Fonts/arialbd.ttf")

    if not font_path.exists():
        raise FileNotFoundError(
            "File unfound"
        )

    pdfmetrics.registerFont(TTFont("Arial", str(font_path)))

    if bold_font_path.exists():
        pdfmetrics.registerFont(
            TTFont("Arial-Bold", str(bold_font_path))
        )
        return "Arial-Bold"
    return "Arial"
def export_to_pdf(specification):
    EXPORT_DIR.mkdir(exist_ok=True)
    bold_font = register_pdf_font()

    filename = create_filename(
        specification["overview"]["title"],
        "pdf"
    )
    path = EXPORT_DIR / filename
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        fontName="Arial-Bold",
        fontSize=20,
        leading=26,
        alignment=1,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        fontName="Arial-Bold",
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        fontName="Arial",
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    story = []

    # Титульный лист
    cover_title_style = ParagraphStyle(
        "CoverTitle",
        fontName="Arial-Bold",
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        spaceAfter=40
    )

    cover_project_style = ParagraphStyle(
        "CoverProject",
        fontName="Arial-Bold",
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=30
    )

    cover_info_style = ParagraphStyle(
        "CoverInfo",
        fontName="Arial",
        fontSize=11,
        leading=18,
        alignment=TA_CENTER
    )

    story.append(Spacer(1, 150))

    story.append(
        Paragraph("ТЕХНИЧЕСКОЕ ЗАДАНИЕ", cover_title_style)
    )

    project_name = specification["overview"]["title"]

    story.append(
        Paragraph(project_name, cover_project_style)
    )

    story.append(Spacer(1, 100))

    story.append(
        Paragraph(
            f"Дата создания: {datetime.now().strftime('%d.%m.%Y')}",
            cover_info_style
        )
    )

    story.append(
        Paragraph("Версия документа: 1.0", cover_info_style)
    )

    story.append(PageBreak())
    def add_text(text, style = normal_style):
        from xml.sax.saxutils import escape
        story.append(
            Paragraph(escape(text), style)
        )
    story.append(
        Paragraph("Техническое задание", title_style)
    )
    overview = specification["overview"]

    story.append(
        Paragraph("1. Общая информация", heading_style)
    )

    for key, value in overview.items():
        add_text(f"{key}: {value}")

    story.append(
        Paragraph("2.Функциональные требования", heading_style)
    )
    functional_requirements = specification["functional_requirements"]

    table_data = [[
        "ID",
        "Название функции",
        "Описание",
        "Приоритет"
    ]]
    for index,item in enumerate(functional_requirements,start=1):
        table_data.append([
            f"FR-{index:03d}",
            Paragraph(str(item["name"]),normal_style),
            Paragraph(str(item["description"]),normal_style),
            Paragraph(str(item["priority"]),normal_style)
        ])
    requirements_table = Table(
        table_data,
        colWidths=[45, 110, 245, 75],
        repeatRows=1
    )
    requirements_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(requirements_table)
    story.append(Spacer(1, 15))

    story.append(
        Paragraph("3. Технические требования", heading_style)
    )

    technical_requirements = specification["technical_requirements"]

    if isinstance(technical_requirements, dict):

        for key, value in technical_requirements.items():
            add_text(f"{key}: {format_value(value)}")

    elif isinstance(technical_requirements, list):

        for item in technical_requirements:
            add_text(f"• {format_value(item)}")

    else:
        add_text(format_value(technical_requirements))

    story.append(
        Paragraph("4. Критерии приёмки", heading_style)
    )

    for item in specification["acceptance_criterion"]:
        story.append(
            Paragraph(item["requirement"], heading_style)
        )
        add_text(item["expected_result"])

    story.append(
        Paragraph("5. План разработки", heading_style)
    )

    for index, step in enumerate(
            specification["develop_plan"],
            start=1
    ):
        add_text(f"{index}. {step}")

    pdf = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    pdf.build(story)

    print(f"\nPDF успешно сохранён: {path}")

    return path

