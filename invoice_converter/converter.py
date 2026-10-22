import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader, PdfWriter


FONT_NAME = "Helvetica"
FONT_SIZE = 10
LINE_HEIGHT = FONT_SIZE * 1.3


def _strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _walk_element(element: ET.Element, indent: int = 0) -> list[str]:
    lines: list[str] = []
    tag = _strip_namespace(element.tag)
    prefix = "  " * indent
    if element.text and element.text.strip():
        lines.append(f"{prefix}<{tag}> {element.text.strip()}")
    else:
        lines.append(f"{prefix}<{tag}>")
    for key, value in element.attrib.items():
        lines.append(f"{prefix}  @{key}: {value}")
    for child in element:
        lines.extend(_walk_element(child, indent + 1))
    return lines


def convert_xml_to_pdf(xml_path: str, output_pdf_path: str, title: str | None = None) -> None:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    lines = [f"XML Invoice: {title or Path(xml_path).name}", ""]
    lines.extend(_walk_element(root))
    Path(output_pdf_path).parent.mkdir(parents=True, exist_ok=True)

    canvas = Canvas(output_pdf_path, pagesize=letter)
    width, height = letter
    left_margin = 50
    right_margin = 50
    top_margin = 50
    bottom_margin = 50
    usable_width = width - left_margin - right_margin
    max_chars = 70

    def _new_page(page_title: str | None = None) -> int:
        canvas.showPage()
        canvas.setFont(FONT_NAME, 12)
        canvas.drawString(left_margin, height - top_margin, page_title or "Factura XML convertido a PDF")
        canvas.setFont(FONT_NAME, FONT_SIZE)
        return height - top_margin - LINE_HEIGHT * 2

    canvas.setFont(FONT_NAME, 12)
    canvas.drawString(left_margin, height - top_margin, title or "Factura XML convertido a PDF")
    y_position = height - top_margin - LINE_HEIGHT * 2
    canvas.setFont(FONT_NAME, FONT_SIZE)

    for line in lines:
        if not line.strip():
            y_position -= LINE_HEIGHT
            continue
        wrapped = textwrap.wrap(
            line,
            width=max_chars,
            break_long_words=True,
            break_on_hyphens=False,
        )
        for wrapped_line in wrapped:
            if y_position < bottom_margin + LINE_HEIGHT:
                y_position = _new_page(title)
            canvas.drawString(left_margin, y_position, wrapped_line)
            y_position -= LINE_HEIGHT
    canvas.save()


def merge_pdfs(pdf_paths: list[str], output_path: str) -> None:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    for pdf_path in pdf_paths:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            writer.add_page(page)
    with output_file.open("wb") as output_stream:
        writer.write(output_stream)
