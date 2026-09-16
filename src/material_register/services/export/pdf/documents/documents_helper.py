from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Paragraph


def paragraph_style(
    font_name: str,
    font_size: int,
    alignment: str,
) -> ParagraphStyle:
    alignments = {
        "left": TA_LEFT,
        "center": TA_CENTER,
        "right": TA_RIGHT,
        "justify": TA_JUSTIFY,
    }
    return ParagraphStyle(
        name="ParagraphStyle",
        fontName=font_name,
        fontSize=font_size,
        alignment=alignments[alignment],
    )


def create_horizontal_line(
    width: str = "100%",
    thickness: int = 2,
    space_before: int = 5,
    space_after: int = 5,
) -> HRFlowable:
    return HRFlowable(
        width=width,
        thickness=thickness,
        spaceBefore=space_before,
        spaceAfter=space_after,
    )


def create_header(
    title_text: str,
    branch_text: str,
    branch_name: str,
    address_text: str,
    address: str,
    document_text: str,
    document: str,
) -> list[Paragraph]:
    title = Paragraph(
        title_text,
        style=paragraph_style("Helvetica", 15, "center"),
    )
    branch_name = Paragraph(
        f"{branch_name}: {branch_text}",
        style=paragraph_style("Helvetica", 13, "left"),
    )
    branch_address = Paragraph(
        f"{address_text}: {address}",
        style=paragraph_style("Helvetica", 13, "left"),
    )
    branch_document = Paragraph(
        f"{document_text}: {document}",
        style=paragraph_style("Helvetica", 13, "left"),
    )
    return [
        title,
        create_horizontal_line(),
        branch_name,
        branch_address,
        branch_document,
    ]
