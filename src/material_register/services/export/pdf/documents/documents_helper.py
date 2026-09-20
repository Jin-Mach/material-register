from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
)

from material_register.domain.branch_dataclass import BranchDataclass
from material_register.domain.transaction_dataclass import Transaction
from material_register.services.export.config.font_constants import (
    BLACK_COLOR,
    BOLD_FONT,
    HEADER_FONT_SIZE,
    REGULAR_FONT,
    STANDARD_FONT_SIZE,
)
from material_register.utils.formatting_utils import format_datetime_to_locale

_ERROR_TEXT = "N/A"


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
    transaction: Transaction,
    branch_settings: BranchDataclass,
    export_texts: dict[str, str],
) -> list:
    transaction_id_text = export_texts.get("transactionIdText", _ERROR_TEXT)
    company_text = export_texts.get("companyText", _ERROR_TEXT)
    branch_text = export_texts.get("branchText", _ERROR_TEXT)
    address_text = export_texts.get("addressText", _ERROR_TEXT)
    company_id_text = export_texts.get(
        "companyIdText",
        _ERROR_TEXT,
    )
    transaction_id = transaction.transaction_id or 0
    company_name = branch_settings.company_name or ""
    branch_name = branch_settings.branch_name or ""
    branch_address = branch_settings.branch_address or ""
    company_id = branch_settings.company_id or ""
    transaction_number = Paragraph(
        f"{transaction_id_text} {transaction_id:06d}",
        style=paragraph_style(BOLD_FONT, HEADER_FONT_SIZE, "right"),
    )
    header_title = Table([["", transaction_number]], colWidths=["50%", "50%"])
    company_info = Table(
        [
            [
                Paragraph(
                    f"{company_text} {company_name}",
                    style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
                )
            ],
            [
                Paragraph(
                    f"{branch_text} {branch_name}",
                    style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
                )
            ],
            [
                Paragraph(
                    f"{address_text} {branch_address}",
                    style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
                )
            ],
            [
                Paragraph(
                    f"{company_id_text} {company_id}",
                    style=paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
                )
            ],
        ],
        colWidths=["100%"],
    )
    company_info.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, HexColor(BLACK_COLOR)),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [header_title, company_info]


def create_transaction_customer_section(
    transaction: Transaction,
    export_texts: dict[str, str],
) -> Table:
    data = [
        [
            Paragraph(
                f"{export_texts.get('transactionTypeText', _ERROR_TEXT)} "
                f"{export_texts.get(transaction.transaction_type, '')}",
                paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
            ),
            Paragraph(
                f"{export_texts.get('createdAtText', _ERROR_TEXT)} "
                f"{format_datetime_to_locale(transaction.transaction_created_at)}",
                paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "right"),
            ),
        ],
        [
            Paragraph(
                f"{export_texts.get('customerNameText', _ERROR_TEXT)} "
                f"{transaction.customer_name}",
                paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
            ),
            "",
        ],
        [
            Paragraph(
                f"{export_texts.get('addressText', _ERROR_TEXT)} "
                f"{transaction.customer_address}",
                paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
            ),
            "",
        ],
        [
            Paragraph(
                f"{export_texts.get('documentNumberText', _ERROR_TEXT)} "
                f"{transaction.customer_document_number}",
                paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
            ),
            "",
        ],
    ]
    table = Table(
        data,
        colWidths=["50%", "50%"],
    )
    table.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 1), (1, 1)),
                ("SPAN", (0, 2), (1, 2)),
                ("SPAN", (0, 3), (1, 3)),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("BOX", (0, 0), (-1, -1), 0.6, HexColor(BLACK_COLOR)),
            ]
        )
    )
    return table


def create_footer(
    canvas: Canvas,
    document: SimpleDocTemplate,
    export_texts: dict[str, str],
) -> None:
    canvas.saveState()
    canvas.setFont(REGULAR_FONT, 8)
    canvas.drawString(
        A4[0] // 2,
        10 * mm,
        f"{export_texts.get('pageText', _ERROR_TEXT)} {document.page}",
    )
    canvas.restoreState()
