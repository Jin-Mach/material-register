from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
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
    BOLD_FONT,
    HEADER_FONT_SIZE,
    REGULAR_FONT,
    STANDARD_FONT_SIZE,
    TOTAL_FONT_SIZE,
)
from material_register.services.export.pdf.documents.documents_helper import (
    create_header,
    create_horizontal_line,
    paragraph_style,
)
from material_register.utils.formatting_utils import (
    format_current_datetime_to_locale,
    format_datetime_to_locale,
    format_number_to_locale,
)


class TransactionDocumentIn:
    ERROR_TEXT = "N/A"

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
                export_texts.get("titleText", TransactionDocumentIn.ERROR_TEXT),
                export_texts.get("companyText", TransactionDocumentIn.ERROR_TEXT),
                branch_settings.company_name or "",
                export_texts.get("branchText", TransactionDocumentIn.ERROR_TEXT),
                branch_settings.branch_name or "",
                export_texts.get("addressText", TransactionDocumentIn.ERROR_TEXT),
                branch_settings.branch_address or "",
                export_texts.get("companyIdText", TransactionDocumentIn.ERROR_TEXT),
                branch_settings.company_id or "",
            )
        )
        content.append(create_horizontal_line())
        content.append(
            TransactionDocumentIn._create_transaction_info(transaction, export_texts)
        )
        content.append(create_horizontal_line())
        content.extend(
            TransactionDocumentIn._create_customer_section(transaction, export_texts)
        )
        content.append(create_horizontal_line())
        total_price, items_table = TransactionDocumentIn._create_items_table(
            items_data, export_texts
        )
        content.append(items_table)
        content.append(create_horizontal_line())
        content.append(
            TransactionDocumentIn._create_total_price_section(total_price, export_texts)
        )
        content.append(create_horizontal_line())
        content.append(TransactionDocumentIn._create_signature_section(export_texts))
        document.build(
            content,
            onFirstPage=lambda canvas, doc: TransactionDocumentIn._create_footer(
                canvas, doc, export_texts
            ),
            onLaterPages=lambda canvas, doc: TransactionDocumentIn._create_footer(
                canvas, doc, export_texts
            ),
        )
        return pdf_buffer.getvalue()

    @staticmethod
    def _create_transaction_info(
        transaction: Transaction,
        export_texts: dict[str, str],
    ) -> Table:
        data = [
            [
                Paragraph(
                    f"{export_texts.get('transactionTypeText', TransactionDocumentIn.ERROR_TEXT)} "
                    f"{export_texts.get(transaction.transaction_type, '')}",
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
                ),
                "",
            ],
            [
                Paragraph(
                    f"{export_texts.get('paymentTypeText', TransactionDocumentIn.ERROR_TEXT)} "
                    f"{export_texts.get(transaction.payment_type, '')}",
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
                ),
                Paragraph(
                    f"{export_texts.get('createdAtText', TransactionDocumentIn.ERROR_TEXT)} "
                    f"{format_datetime_to_locale(transaction.transaction_created_at)}",
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "right"),
                ),
            ],
        ]
        table = Table(
            data,
            colWidths=[83 * mm, 83 * mm],
        )
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return table

    @staticmethod
    def _create_customer_section(
        transaction: Transaction,
        export_texts: dict[str, str],
    ) -> list[Paragraph]:
        customer_name = Paragraph(
            f"{export_texts.get('customerNameText', TransactionDocumentIn.ERROR_TEXT)} "
            f"{transaction.customer_name}",
            paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
        )
        customer_address = Paragraph(
            f"{export_texts.get('addressText', TransactionDocumentIn.ERROR_TEXT)} "
            f"{transaction.customer_address}",
            paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
        )
        customer_document = Paragraph(
            f"{export_texts.get('documentNumberText', TransactionDocumentIn.ERROR_TEXT)} "
            f"{transaction.customer_document_number}",
            paragraph_style(REGULAR_FONT, HEADER_FONT_SIZE, "left"),
        )
        return [customer_name, customer_address, customer_document]

    @staticmethod
    def _create_items_table(
        items_data: list[TransactionItemDetail],
        export_texts: dict[str, str],
    ) -> tuple[float, Table]:
        total_price = 0
        data = [
            [
                Paragraph(
                    export_texts.get("categoryText", TransactionDocumentIn.ERROR_TEXT),
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
                ),
                Paragraph(
                    export_texts.get("commodityText", TransactionDocumentIn.ERROR_TEXT),
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
                ),
                Paragraph(
                    export_texts.get("quantityText", TransactionDocumentIn.ERROR_TEXT),
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "right"),
                ),
                Paragraph(
                    export_texts.get(
                        "pricePerUnitText", TransactionDocumentIn.ERROR_TEXT
                    ),
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "right"),
                ),
                Paragraph(
                    export_texts.get(
                        "totalPriceText", TransactionDocumentIn.ERROR_TEXT
                    ),
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "right"),
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
            colWidths=[42 * mm, 42 * mm, 25 * mm, 25 * mm, 30 * mm],
            repeatRows=1,
        )
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (1, -1), "LEFT"),
                    ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return total_price, table

    @staticmethod
    def _create_total_price_section(
        total_price: float,
        export_texts: dict[str, str],
    ) -> Paragraph:
        price = Paragraph(
            f"{export_texts.get('summaryPriceText', TransactionDocumentIn.ERROR_TEXT)} "
            f"{format_number_to_locale(total_price)} "
            f"{export_texts.get('currencySuffix', '')}",
            paragraph_style(BOLD_FONT, TOTAL_FONT_SIZE, "right"),
        )
        return price

    @staticmethod
    def _create_signature_section(
        export_texts: dict[str, str],
    ) -> TopPadder:
        data = [
            [
                Paragraph(
                    f"{export_texts.get('createdAtDateTimeText', TransactionDocumentIn.ERROR_TEXT)} "
                    f"{format_current_datetime_to_locale()}",
                    paragraph_style(REGULAR_FONT, STANDARD_FONT_SIZE, "left"),
                ),
                [
                    create_horizontal_line(),
                    Paragraph(
                        export_texts.get(
                            "signatureText", TransactionDocumentIn.ERROR_TEXT
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

    @staticmethod
    def _create_footer(
        canvas: Canvas,
        document: SimpleDocTemplate,
        export_texts: dict[str, str],
    ) -> None:
        canvas.saveState()
        canvas.setFont(REGULAR_FONT, 8)
        canvas.drawString(
            A4[0] // 2,
            10 * mm,
            f"{export_texts.get('pageText', TransactionDocumentIn.ERROR_TEXT)} "
            f"{document.page}",
        )
        canvas.restoreState()
