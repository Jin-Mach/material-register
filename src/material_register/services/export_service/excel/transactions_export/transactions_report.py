from material_register.domain.export_dataclass.transactions_dataclass import (
    TransactionsExportDay,
)


class TransactionsReport:
    @staticmethod
    def get_split_data(
        in_data: list[TransactionsExportDay],
    ) -> dict[str, list[TransactionsExportDay]]:
        report_data = {}
        for transaction_day in in_data:
            date = transaction_day.transaction_date.split("-")
            sheet_date = f"{date[1]}-{date[0]}"
            if sheet_date not in report_data:
                report_data[sheet_date] = []
            report_data[sheet_date].append(transaction_day)
        return report_data
