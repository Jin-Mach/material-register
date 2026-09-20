from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    TopPadder,
)

from material_register.domain.branch_dataclass import BranchDataclass
from material_register.domain.transaction_dataclass import Transaction
from material_register.domain.transaction_item_detail_dataclass import (
    TransactionItemDetail,
)
from material_register.services.export.config.font_constants import (
    BLACK_COLOR,
    BOLD_FONT,
    GREY_COLOR,
    REGULAR_FONT,
    STANDARD_FONT_SIZE,
    TOTAL_FONT_SIZE,
)
from material_register.services.export.pdf.documents.documents_helper import (
    create_footer,
    create_header,
    create_horizontal_line,
    create_transaction_customer_section,
    paragraph_style,
)
from material_register.utils.formatting_utils import (
    format_current_datetime_to_locale,
    format_number_to_locale,
)


class TransactionDocumentIn:
    _ERROR_TEXT = "N/A"

    @staticmethod
    def create_document(
        transaction: Transaction,
        items_data: list[TransactionItemDetail],
        branch_settings: BranchDataclass,
        export_texts: dict[str, dict[str, str]],
    ) -> bytes:
        export_texts = export_texts.get("TransactionDocument", {})
        pdf_buffer = BytesIO()
        document = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            rightMargin=20 * mm,
            bottomMargin=20 * mm,
        )
        content = []
        content.extend(
            create_header(
                transaction,
                branch_settings,
                export_texts,
            )
        )
        content.append(Spacer(1, 5 * mm))
        content.append(
            create_transaction_customer_section(
                transaction,
                export_texts,
            )
        )
        content.append(Spacer(1, 5 * mm))
        total_price, items_table = TransactionDocumentIn._create_items_table(
            items_data, export_texts
        )
        content.append(items_table)
        content.append(Spacer(1, 5 * mm))
        content.append(
            TransactionDocumentIn._create_total_price_section(total_price, export_texts)
        )
        content.append(Spacer(1, 5 * mm))
        content.append(TransactionDocumentIn._create_signature_section(export_texts))
        document.build(
            content,
            onFirstPage=lambda canvas, doc: create_footer(
                canvas,
                doc,
                export_texts,
            ),
            onLaterPages=lambda canvas, doc: create_footer(
                canvas,
                doc,
                export_texts,
            ),
        )
        return pdf_buffer.getvalue()

    @staticmethod
    def _create_items_table(
        items_data: list[TransactionItemDetail],
        export_texts: dict[str, str],
    ) -> tuple[float, Table]:
        total_price = 0
        data = [
            [
                Paragraph(
                    export_texts.get("categoryText", TransactionDocumentIn._ERROR_TEXT),
                    paragraph_style(BOLD_FONT, STANDARD_FONT_SIZE, "left"),
                ),
                Paragraph(
                    export_texts.get(
                        "commodityText", TransactionDocumentIn._ERROR_TEXT
                    ),
                    paragraph_style(BOLD_FONT, STANDARD_FONT_SIZE, "left"),
                ),
                Paragraph(
                    export_texts.get("quantityText", TransactionDocumentIn._ERROR_TEXT),
                    paragraph_style(BOLD_FONT, STANDARD_FONT_SIZE, "right"),
                ),
                Paragraph(
                    export_texts.get(
                        "pricePerUnitText", TransactionDocumentIn._ERROR_TEXT
                    ),
                    paragraph_style(BOLD_FONT, STANDARD_FONT_SIZE, "right"),
                ),
                Paragraph(
                    export_texts.get(
                        "totalPriceText", TransactionDocumentIn._ERROR_TEXT
                    ),
                    paragraph_style(BOLD_FONT, STANDARD_FONT_SIZE, "right"),
                ),
            ]
        ]
        for item in items_data:
            current_price = float(round(item.unit_count * item.price_per_unit, 1))
            total_price += current_price
            data.append(
                [
                    Paragraph(
                        item.category_name,
                        paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
                    ),
                    Paragraph(
                        item.commodity_name,
                        paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
                    ),
                    Paragraph(
                        f"{format_number_to_locale(item.unit_count)} "
                        f"{item.commodity_suffix}",
                        paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "right"),
                    ),
                    Paragraph(
                        f"{format_number_to_locale(item.price_per_unit)} "
                        f"{export_texts.get('currencySuffix', '')}",
                        paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "right"),
                    ),
                    Paragraph(
                        f"{format_number_to_locale(current_price)} "
                        f"{export_texts.get('currencySuffix', '')}",
                        paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "right"),
                    ),
                ]
            )
        table = Table(
            data,
            colWidths=[40 * mm, 40 * mm, 25 * mm, 30 * mm, 30 * mm],
            repeatRows=1,
        )
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (1, -1), "LEFT"),
                    ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor(GREY_COLOR)),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, HexColor(BLACK_COLOR)),
                    ("BOX", (0, 0), (-1, -1), 0.6, HexColor(BLACK_COLOR)),
                ]
            )
        )
        return total_price, table

    @staticmethod
    def _create_total_price_section(
        total_price: float,
        export_texts: dict[str, str],
    ) -> Table:
        text = (
            f"{export_texts.get('summaryPriceText', TransactionDocumentIn._ERROR_TEXT)} "
            f"{format_number_to_locale(total_price)} "
            f"{export_texts.get('currencySuffix', '')}"
        )
        text_width = stringWidth(
            text,
            BOLD_FONT,
            TOTAL_FONT_SIZE,
        )
        box_width = text_width + 10
        price = Paragraph(
            text,
            paragraph_style(BOLD_FONT, TOTAL_FONT_SIZE, "right"),
        )
        table = Table(
            [[price]],
            colWidths=[box_width],
        )
        table.hAlign = "RIGHT"
        table.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("BACKGROUND", (0, 0), (0, 0), HexColor(GREY_COLOR)),
                    ("BOX", (0, 0), (0, 0), 1.2, HexColor(BLACK_COLOR)),
                ]
            )
        )
        return table

    @staticmethod
    def _create_signature_section(
        export_texts: dict[str, str],
    ) -> TopPadder:
        data = [
            [
                Paragraph(
                    f"{export_texts.get('createdAtDateTimeText', TransactionDocumentIn._ERROR_TEXT)} "
                    f"{format_current_datetime_to_locale()}",
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
                ),
                [
                    create_horizontal_line(),
                    Paragraph(
                        export_texts.get(
                            "signatureText", TransactionDocumentIn._ERROR_TEXT
                        ),
                        paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "center"),
                    ),
                ],
            ]
        ]
        table = Table(
            data,
            colWidths=[83 * mm, 83 * mm],
        )
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return TopPadder(table)
