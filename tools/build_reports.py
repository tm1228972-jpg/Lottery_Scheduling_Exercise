"""Export the repository's concise Markdown reports as Word and PDF drafts.

The exported files are formatted with RTL handling for Persian and marked as
short drafts. All six exercise report/article exports are checked against the
approximately 40-page target and explicitly marked as far below target. The
script never pads or repeats content to manufacture a page count.

Install the optional dependencies with `python -m pip install -e '.[reports]'`.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
import textwrap

from arabic_reshaper import reshape
from bidi.algorithm import get_display
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGB
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.platypus import (
    Image as PdfImage,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table as PdfTable,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
TARGET_PAGES = 40
PAGE_TARGET_EXERCISES = {"01", "02", "03", "04", "05", "06"}
DRAFT_40_EN = (
    "SHORT EVIDENCE-BASED DRAFT — this export is far below the requested "
    "40-page target. No filler has been added. Expand only with verified course "
    "material, approved sources, and supported results."
)
DRAFT_40_FA = (
    "پیش‌نویس فنی کوتاه — این خروجی بسیار کمتر از هدف ۴۰صفحه‌ای درخواستی است. "
    "برای ساخت صفحه متن تکراری یا نتیجهٔ ساختگی اضافه نشده است."
)


def draft_notice(language: str) -> str:
    return DRAFT_40_FA if language == "fa" else DRAFT_40_EN

REPORTS = [
    ("01", "01-lottery-introduction", "docs/reports/report-fa.md", "report-fa", "fa"),
    ("01", "01-lottery-introduction", "docs/reports/report-en.md", "report-en", "en"),
    ("02", "02-edf-rm-comparison", "docs/reports/report-fa.md", "report-fa", "fa"),
    ("02", "02-edf-rm-comparison", "docs/reports/report-en.md", "report-en", "en"),
    ("03", "03-edf-rm-three-processes", "docs/reports/report-fa.md", "report-fa", "fa"),
    ("03", "03-edf-rm-three-processes", "docs/reports/report-en.md", "report-en", "en"),
    ("04", "04-readers-writers-comparison", "docs/reports/report-fa.md", "report-fa", "fa"),
    ("04", "04-readers-writers-comparison", "docs/reports/report-en.md", "report-en", "en"),
    ("05", "05-lottery-scheduling-clip", "docs/reports/report-fa.md", "report-fa", "fa"),
    ("05", "05-lottery-scheduling-clip", "docs/reports/report-en.md", "report-en", "en"),
    ("06", "06-lottery-seminar", "docs/article-fa.md", "article-fa", "fa"),
    ("06", "06-lottery-seminar", "docs/article-en.md", "article-en", "en"),
]


@dataclass
class Element:
    kind: str
    value: object
    level: int = 0


def is_rtl(language: str) -> bool:
    return language == "fa"


def visual_fa(text: str) -> str:
    return get_display(reshape(text))


def clean_inline(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\1", text)
    # Preserve a readable label in exports; Markdown remains the source of the
    # hyperlink target, and local paths should not clutter the rendered page.
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"<(https?://[^>]+)>", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_table(lines: list[str]) -> list[list[str]]:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        rows.append([clean_inline(cell) for cell in cells])
    return rows


def parse_markdown(path: Path) -> list[Element]:
    lines = path.read_text(encoding="utf-8").splitlines()
    elements: list[Element] = []
    i = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            text = clean_inline(" ".join(paragraph))
            if text:
                elements.append(Element("paragraph", text))
            paragraph = []

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped or stripped in ("</div>", "---") or stripped.startswith("<div"):
            flush_paragraph()
            i += 1
            continue
        if stripped.startswith("```"):
            flush_paragraph()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i].rstrip())
                i += 1
            elements.append(Element("code", "\n".join(code_lines)))
            i += 1
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            elements.append(Element("table", parse_table(table_lines)))
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            elements.append(Element("heading", clean_inline(heading.group(2)), len(heading.group(1))))
            i += 1
            continue
        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if image:
            flush_paragraph()
            elements.append(Element("image", (image.group(1), image.group(2))))
            i += 1
            continue
        bullet = re.match(r"^(?:[-*+]\s+|\d+\.\s+)(.*)$", stripped)
        if bullet:
            flush_paragraph()
            items = []
            while i < len(lines):
                match = re.match(r"^\s*(?:[-*+]\s+|\d+\.\s+)(.*)$", lines[i])
                if not match:
                    break
                items.append(clean_inline(match.group(1)))
                i += 1
            elements.append(Element("list", items))
            continue
        paragraph.append(stripped)
        i += 1
    flush_paragraph()
    return elements


def heading_data(elements: list[Element]) -> tuple[str, list[str]]:
    headings = [element for element in elements if element.kind == "heading"]
    title = str(headings[0].value) if headings else "Technical report"
    outline = [str(h.value) for h in headings[1:] if h.level <= 2]
    return title, outline


def pdf_paragraph(text: str, style: ParagraphStyle, rtl: bool = False) -> Paragraph:
    text = clean_inline(text)
    if rtl:
        # Wrap logical Persian text before shaping each line, preserving correct
        # joining and bidirectional order without mirroring glyphs.
        logical_lines = simpleSplit(text, style.fontName, style.fontSize, style.width or 15 * cm)
        rendered = "<br/>".join(escape(visual_fa(line)) for line in logical_lines)
    else:
        rendered = escape(text)
    return Paragraph(rendered, style)


def set_docx_rtl(paragraph, rtl: bool) -> None:
    if rtl:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_pr = paragraph._p.get_or_add_pPr()
        bidi = OxmlElement("w:bidi")
        bidi.set(qn("w:val"), "1")
        p_pr.append(bidi)
    else:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT


def set_run_properties(run, rtl: bool, size: int = 10, bold: bool = False, color="25364B", font="Arial") -> None:
    run.font.name = font
    run.font.size = DocxPt(size)
    run.font.bold = bold
    run.font.color.rgb = DocxRGB.from_string(color)
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is not None:
        r_fonts.set(qn("w:cs"), "Arial")
        r_fonts.set(qn("w:eastAsia"), "Arial")
    if rtl:
        rtl_tag = OxmlElement("w:rtl")
        rtl_tag.set(qn("w:val"), "1")
        r_pr.append(rtl_tag)


def add_docx_text(document, text: str, rtl: bool, style=None, size=10, bold=False, color="25364B", font="Arial"):
    paragraph = document.add_paragraph(style=style)
    set_docx_rtl(paragraph, rtl)
    paragraph.paragraph_format.space_before = DocxPt(0)
    paragraph.paragraph_format.space_after = DocxPt(5)
    paragraph.paragraph_format.line_spacing = 1.05
    run = paragraph.add_run(clean_inline(text))
    set_run_properties(run, rtl, size=size, bold=bold, color=color, font=font)
    return paragraph


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def add_docx_table(document, rows: list[list[str]], rtl: bool) -> None:
    if not rows:
        return
    column_count = max(len(row) for row in rows)
    table = document.add_table(rows=0, cols=column_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Shading Accent 1"
    tbl_pr = table._tbl.tblPr
    if rtl:
        bidi = OxmlElement("w:bidiVisual")
        bidi.set(qn("w:val"), "1")
        tbl_pr.append(bidi)
    for row_index, row_data in enumerate(rows):
        values = list(row_data) + [""] * (column_count - len(row_data))
        row = table.add_row()
        for cell, value in zip(row.cells, values):
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index == 0:
                set_cell_shading(cell, "1B4965")
            paragraph = cell.paragraphs[0]
            set_docx_rtl(paragraph, rtl)
            paragraph.paragraph_format.space_after = DocxPt(2)
            run = paragraph.add_run(value)
            set_run_properties(run, rtl, size=8.5, bold=(row_index == 0), color=("FFFFFF" if row_index == 0 else "25364B"))
    document.add_paragraph().paragraph_format.space_after = DocxPt(3)


def add_page_field(paragraph) -> None:
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr)
    run._r.append(fld_char2)


def build_docx(exercise: str, source: Path, output: Path, language: str, elements: list[Element], title: str, outline: list[str]) -> None:
    rtl = is_rtl(language)
    document = Document()
    section = document.sections[0]
    section.page_width = DocxInches(8.27)
    section.page_height = DocxInches(11.69)
    section.top_margin = DocxInches(0.66)
    section.bottom_margin = DocxInches(0.62)
    section.left_margin = DocxInches(0.72)
    section.right_margin = DocxInches(0.72)

    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = DocxPt(10)
    header = section.header.paragraphs[0]
    set_docx_rtl(header, rtl)
    header_run = header.add_run("Lottery Scheduling Exercise · Evidence-based draft" if not rtl else "تمرین زمان‌بندی لاتاری · پیش‌نویس مستند")
    set_run_properties(header_run, rtl, size=8, color="64748B")
    footer = section.footer.paragraphs[0]
    set_docx_rtl(footer, rtl)
    footer_run = footer.add_run("SHORT DRAFT · " if not rtl else "پیش‌نویس کوتاه · ")
    set_run_properties(footer_run, rtl, size=8, color="DF6B63")
    add_page_field(footer)

    title_par = document.add_paragraph()
    set_docx_rtl(title_par, rtl)
    title_par.paragraph_format.space_before = DocxPt(6)
    title_par.paragraph_format.space_after = DocxPt(8)
    run = title_par.add_run(title)
    set_run_properties(run, rtl, size=20, bold=True, color="14243A")
    notice = draft_notice(language)
    add_docx_text(document, notice, rtl, size=8.5, bold=True, color="A94442")

    if outline:
        label = "فهرست سرفصل‌ها (بدون شماره صفحه)" if rtl else "Contents (section outline; page numbers are not generated)"
        add_docx_text(document, label, rtl, size=11, bold=True, color="1B4965")
        for entry in outline:
            add_docx_text(document, "• " + entry, rtl, size=8.5, color="64748B")

    first_h1_skipped = False
    for element in elements:
        if element.kind == "heading":
            if not first_h1_skipped and element.level == 1:
                first_h1_skipped = True
                continue
            level = min(max(element.level, 2), 4)
            paragraph = document.add_paragraph()
            set_docx_rtl(paragraph, rtl)
            paragraph.paragraph_format.keep_with_next = True
            paragraph.paragraph_format.space_before = DocxPt(9 if level == 2 else 5)
            paragraph.paragraph_format.space_after = DocxPt(4)
            run = paragraph.add_run(str(element.value))
            set_run_properties(run, rtl, size=(14 if level == 2 else 11), bold=True, color="1B4965")
        elif element.kind == "paragraph":
            add_docx_text(document, str(element.value), rtl)
        elif element.kind == "list":
            for item in element.value:
                add_docx_text(document, "• " + str(item), rtl, size=9.5)
        elif element.kind == "table":
            add_docx_table(document, element.value, rtl)
        elif element.kind == "code":
            table = document.add_table(rows=1, cols=1)
            cell = table.cell(0, 0)
            set_cell_shading(cell, "F1F5F9")
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for index, line in enumerate(str(element.value).splitlines()):
                if index:
                    paragraph.add_run().add_break()
                run = paragraph.add_run(line)
                set_run_properties(run, False, size=8, color="25364B", font="Consolas")
            document.add_paragraph().paragraph_format.space_after = DocxPt(2)
        elif element.kind == "image":
            alt, target = element.value
            image_path = (source.parent / target).resolve()
            if image_path.exists():
                paragraph = document.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.add_run().add_picture(str(image_path), width=DocxInches(5.7))
                caption = document.add_paragraph()
                caption.alignment = WD_ALIGN_PARAGRAPH.RIGHT if rtl else WD_ALIGN_PARAGRAPH.CENTER
                run = caption.add_run(alt)
                set_run_properties(run, rtl, size=8, color="64748B")
    document.core_properties.title = title
    document.core_properties.subject = "Short working draft; verify against the exercise-specific rubric"
    document.core_properties.author = "Lottery Scheduling Exercise"
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def pdf_styles(language: str):
    rtl = is_rtl(language)
    base = getSampleStyleSheet()
    alignment = TA_RIGHT if rtl else TA_LEFT
    body = ParagraphStyle(
        "BodyCustom",
        parent=base["BodyText"],
        fontName="DejaVuSans",
        fontSize=9.5,
        leading=13,
        alignment=alignment,
        textColor=colors.HexColor("#25364B"),
        spaceAfter=6,
        wordWrap="CJK",
    )
    h1 = ParagraphStyle("H1Custom", parent=body, fontSize=18, leading=23, textColor=colors.HexColor("#14243A"), spaceAfter=9)
    h2 = ParagraphStyle("H2Custom", parent=body, fontSize=13, leading=17, textColor=colors.HexColor("#1B4965"), spaceBefore=7, spaceAfter=5, keepWithNext=True)
    h3 = ParagraphStyle("H3Custom", parent=h2, fontSize=11, leading=14, spaceBefore=5)
    small = ParagraphStyle("SmallCustom", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#64748B"), spaceAfter=3)
    notice = ParagraphStyle("NoticeCustom", parent=body, fontSize=8.5, leading=12, textColor=colors.HexColor("#A94442"), backColor=colors.HexColor("#FFF3F2"), borderPadding=6, spaceAfter=8)
    code = ParagraphStyle("CodeCustom", parent=body, fontName="DejaVuMono", fontSize=7.2, leading=9, alignment=TA_LEFT, backColor=colors.HexColor("#F1F5F9"), borderPadding=5, spaceBefore=3, spaceAfter=6)
    bullet = ParagraphStyle("BulletCustom", parent=body, leftIndent=(0 if rtl else 12), rightIndent=(12 if rtl else 0), firstLineIndent=(0 if rtl else -8), spaceAfter=4)
    return body, h1, h2, h3, small, notice, code, bullet


def pdf_flowable_text(text: str, style: ParagraphStyle, rtl: bool, max_width: float) -> Paragraph:
    text = clean_inline(text)
    if rtl:
        logical_lines = simpleSplit(text, style.fontName, style.fontSize, max_width)
        rendered = "<br/>".join(escape(visual_fa(line)) for line in logical_lines)
    else:
        rendered = escape(text)
    return Paragraph(rendered, style)


def build_pdf(exercise: str, source: Path, output: Path, language: str, elements: list[Element], title: str, outline: list[str]) -> int:
    rtl = is_rtl(language)
    font_regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font_mono = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    if not font_regular.exists():
        raise FileNotFoundError("DejaVu Sans font is required for the generated PDFs")
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    try:
        pdfmetrics.getFont("DejaVuSans")
    except KeyError:
        pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_regular)))
    try:
        pdfmetrics.getFont("DejaVuMono")
    except KeyError:
        pdfmetrics.registerFont(TTFont("DejaVuMono", str(font_mono if font_mono.exists() else font_regular)))

    body, h1, h2, h3, small, notice, code_style, bullet = pdf_styles(language)
    available_width = A4[0] - 3.4 * cm
    story = [pdf_flowable_text(title, h1, rtl, available_width)]
    story.append(pdf_flowable_text(draft_notice(language), notice, rtl, available_width))
    if outline:
        outline_label = "فهرست سرفصل‌ها (بدون شماره صفحه)" if rtl else "Contents (section outline; page numbers are not generated)"
        story.append(pdf_flowable_text(outline_label, h2, rtl, available_width))
        for entry in outline:
            story.append(pdf_flowable_text("• " + entry, small, rtl, available_width))
        story.append(Spacer(1, 5))

    first_h1_skipped = False
    for element in elements:
        if element.kind == "heading":
            if not first_h1_skipped and element.level == 1:
                first_h1_skipped = True
                continue
            style = h2 if element.level == 2 else h3
            story.append(pdf_flowable_text(str(element.value), style, rtl, available_width))
        elif element.kind == "paragraph":
            story.append(pdf_flowable_text(str(element.value), body, rtl, available_width))
        elif element.kind == "list":
            for item in element.value:
                story.append(pdf_flowable_text("• " + str(item), bullet, rtl, available_width))
        elif element.kind == "code":
            story.append(Preformatted(str(element.value), code_style, maxLineLength=105))
            story.append(Spacer(1, 3))
        elif element.kind == "table":
            rows = element.value
            if not rows:
                continue
            column_count = max(len(row) for row in rows)
            data = []
            for row_index, row in enumerate(rows):
                values = list(row) + [""] * (column_count - len(row))
                if rtl:
                    values.reverse()
                style = small if row_index == 0 else body
                data.append([pdf_flowable_text(value, style, rtl, available_width / column_count - 8) for value in values])
            table = PdfTable(data, colWidths=[available_width / column_count] * column_count, repeatRows=1, hAlign="RIGHT" if rtl else "LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4965")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT" if rtl else "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(KeepTogether([table, Spacer(1, 6)]))
        elif element.kind == "image":
            alt, target = element.value
            image_path = (source.parent / target).resolve()
            if image_path.exists():
                reader = ImageReader(str(image_path))
                width, height = reader.getSize()
                scale = min(available_width / width, 12 * cm / height, 1.0)
                story.append(PdfImage(str(image_path), width=width * scale, height=height * scale, hAlign="CENTER"))
                story.append(pdf_flowable_text(alt, small, rtl, available_width))

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title=title,
        author="Lottery Scheduling Exercise",
        subject="Short working draft; verify against the exercise-specific rubric",
    )

    def on_page(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
        canvas.line(1.7 * cm, A4[1] - 1.25 * cm, A4[0] - 1.7 * cm, A4[1] - 1.25 * cm)
        canvas.setFont("DejaVuSans", 7)
        header = "Lottery Scheduling Exercise · SHORT DRAFT" if not rtl else "تمرین زمان‌بندی لاتاری · پیش‌نویس کوتاه"
        footer = f"Short draft · Page {document.page}" if not rtl else f"پیش‌نویس کوتاه · صفحه {document.page}"
        if rtl:
            canvas.drawRightString(A4[0] - 1.7 * cm, A4[1] - 1.05 * cm, visual_fa(header))
            canvas.drawRightString(A4[0] - 1.7 * cm, 0.85 * cm, visual_fa(footer))
        else:
            canvas.drawString(1.7 * cm, A4[1] - 1.05 * cm, header)
            canvas.drawString(1.7 * cm, 0.85 * cm, footer)
        canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    reader = PdfReader(str(output))
    pages = len(reader.pages)
    if any(not (page.extract_text() or "").strip() for page in reader.pages):
        raise RuntimeError(f"blank PDF page detected in {output}")
    return pages


def main() -> None:
    manifest = {
        "target_pdf_pages_for_exercises": sorted(PAGE_TARGET_EXERCISES),
        "target_pdf_pages": TARGET_PAGES,
        "notice": "All exports are short working drafts and remain below the approximately 40-page target; none is submission-ready.",
        "documents": [],
    }
    for exercise, directory, source_rel, output_stem, language in REPORTS:
        source = ROOT / "assignments" / directory / source_rel
        if not source.exists():
            raise FileNotFoundError(source)
        elements = parse_markdown(source)
        title, outline = heading_data(elements)
        output_dir = ROOT / "assignments" / directory / "docs/reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        docx_path = output_dir / f"{output_stem}.docx"
        pdf_path = output_dir / f"{output_stem}.pdf"
        build_docx(exercise, source, docx_path, language, elements, title, outline)
        pdf_pages = build_pdf(exercise, source, pdf_path, language, elements, title, outline)
        page_target = TARGET_PAGES if exercise in PAGE_TARGET_EXERCISES else None
        manifest["documents"].append({
            "exercise": exercise,
            "language": language,
            "source": str(source.relative_to(ROOT)),
            "docx": str(docx_path.relative_to(ROOT)),
            "pdf": str(pdf_path.relative_to(ROOT)),
            "pdf_pages": pdf_pages,
            "page_target": page_target,
            "meets_page_target": (pdf_pages >= page_target) if page_target is not None else None,
            "submission_ready": False,
        })
        target_text = f"target {page_target} pages" if page_target is not None else "no 40-page target recorded"
        print(f"{exercise}/{language}: {pdf_pages} PDF pages (short draft; {target_text})")
    manifest_path = ROOT / "REPORT_EXPORT_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote report export manifest: {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
