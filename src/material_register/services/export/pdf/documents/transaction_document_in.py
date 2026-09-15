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

from material_register.domain.transaction_dataclass import Transaction
from material_register.domain.transaction_item_detail_dataclass import (
    TransactionItemDetail,
)
from material_register.services.export.pdf.documents.documents_helper import (
    paragraph_style,
    create_horizontal_line,
)


class TransactionDocumentIn:
    @staticmethod
    def create_document(
        transaction: Transaction, items_data: list[TransactionItemDetail]
    ) -> bytes:
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
        content.extend(TransactionDocumentIn._create_header())
        content.append(create_horizontal_line())
        content.append(TransactionDocumentIn._create_transaction_info(transaction))
        content.append(create_horizontal_line())
        content.extend(TransactionDocumentIn._create_customer_section(transaction))
        content.append(create_horizontal_line())
        total_price, items_table = TransactionDocumentIn._create_items_table(items_data)
        content.append(items_table)
        content.append(create_horizontal_line())
        content.append(TransactionDocumentIn._create_total_price_section(total_price))
        content.append(create_horizontal_line())
        content.append(TransactionDocumentIn._create_signature_section())
        document.build(
            content,
            onFirstPage=TransactionDocumentIn._create_footer,
            onLaterPages=TransactionDocumentIn._create_footer,
        )
        return pdf_buffer.getvalue()

    @staticmethod
    def _create_header() -> list[Paragraph]:
        title = Paragraph(
            "Transaction document",
            style=paragraph_style("Helvetica", 15, "center"),
        )
        branch_name = Paragraph(
            "Branch: Some branch name",
            style=paragraph_style("Helvetica", 13, "left"),
        )
        branch_address = Paragraph(
            "Address: Some address",
            style=paragraph_style("Helvetica", 13, "left"),
        )
        branch_document = Paragraph(
            "IČO: 12345",
            style=paragraph_style("Helvetica", 13, "left"),
        )
        return [
            title,
            create_horizontal_line(),
            branch_name,
            branch_address,
            branch_document,
        ]

    @staticmethod
    def _create_transaction_info(transaction: Transaction) -> Table:
        data = [
            [
                f"Trans type: {transaction.transaction_type}",
                f"Date: {transaction.transaction_created_at}",
            ],
            [
                f"Payment: {transaction.payment_type}",
                f"Time: {transaction.transaction_created_at}",
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
    def _create_customer_section(transaction: Transaction) -> list[Paragraph]:
        customer_name = Paragraph(
            f"Customer: {transaction.customer_name}",
            paragraph_style("Helvetica", 13, "left"),
        )
        customer_address = Paragraph(
            f"Address: {transaction.customer_address}",
            paragraph_style("Helvetica", 13, "left"),
        )
        customer_document = Paragraph(
            f"Document: {transaction.customer_document_number}",
            paragraph_style("Helvetica", 13, "left"),
        )
        return [customer_name, customer_address, customer_document]

    @staticmethod
    def _create_items_table(
        items_data: list[TransactionItemDetail],
    ) -> tuple[float, Table]:
        total_price = 0
        data = [["Category", "Item", "Count", "Price per unit", "Price"]]
        for item in items_data:
            current_price = float(round(item.unit_count * item.price_per_unit, 1))
            total_price += current_price
            data.append(
                [
                    Paragraph(
                        item.category_name,
                        paragraph_style("Helvetica", 12, "left"),
                    ),
                    Paragraph(
                        item.commodity_name,
                        paragraph_style("Helvetica", 12, "left"),
                    ),
                    f"{item.unit_count} {item.commodity_suffix}",
                    item.price_per_unit,
                    current_price,
                ]
            )
        table = Table(
            data,
            colWidths=[42 * mm, 42 * mm, 25 * mm, 30 * mm, 25 * mm],
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
    def _create_total_price_section(total_price: float) -> Paragraph:
        price = Paragraph(
            f"Total: {total_price:.1f}",
            paragraph_style("Helvetica", 14, "right"),
        )
        return price

    @staticmethod
    def _create_signature_section() -> TopPadder:
        data = [
            [
                Paragraph(
                    "On Mars: 1.1.2026",
                    paragraph_style("Helvetica", 12, "left"),
                ),
                [
                    create_horizontal_line(),
                    Paragraph(
                        "Signature",
                        paragraph_style("Helvetica", 12, "center"),
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
    def _create_footer(canvas: Canvas, document: SimpleDocTemplate) -> None:
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(A4[0] // 2, 10 * mm, f"Page: {document.page}")
        canvas.restoreState()
