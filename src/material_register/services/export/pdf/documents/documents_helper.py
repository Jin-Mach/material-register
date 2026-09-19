from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Paragraph, Table

from material_register.services.export.config.font_constants import (
    HEADER_FONT_SIZE,
    REGULAR_FONT,
    TITLE_FONT_SIZE,
)


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
    transaction_id_text: str,
    transaction_id: int,
    company_text: str,
    company_name: str,
    branch_text: str,
    branch_name: str,
    address_text: str,
    address: str,
    company_id_text: str,
    company_id: str,
) -> list:
    title = Paragraph(
        title_text,
        style=paragraph_style(REGULAR_FONT, TITLE_FONT_SIZE, "left"),
    )
    transaction_number = Paragraph(
        f"{transaction_id_text} {transaction_id:06d}",
        style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "right"),
    )
    header_title = Table(
        [[title, transaction_number]],
        colWidths=["50%", "50%"],
    )
    company_name_paragraph = Paragraph(
        f"{company_text} {company_name}",
        style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
    )
    branch_name_paragraph = Paragraph(
        f"{branch_text} {branch_name}",
        style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
    )
    branch_address = Paragraph(
        f"{address_text} {address}",
        style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
    )
    branch_company_id = Paragraph(
        f"{company_id_text} {company_id}",
        style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
    )
    return [
        header_title,
        create_horizontal_line(),
        company_name_paragraph,
        branch_name_paragraph,
        branch_address,
        branch_company_id,
    ]
