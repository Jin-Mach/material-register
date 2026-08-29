import pytest

from material_register.domain.export_dataclass.transactions_dataclass import (
    TransactionsExportDay,
)
from material_register.services.export.excel.transactions_export.transactions_report import (
    TransactionsReport,
)


@pytest.fixture
def export_data() -> list[TransactionsExportDay]:
    return [
        TransactionsExportDay(
            transaction_date="2026-07-12",
            transactions_list=[],
        ),
        TransactionsExportDay(
            transaction_date="2026-07-25",
            transactions_list=[],
        ),
        TransactionsExportDay(
            transaction_date="2026-08-01",
            transactions_list=[],
        ),
        TransactionsExportDay(
            transaction_date="2026-08-03",
            transactions_list=[],
        ),
    ]


@pytest.fixture
def result_data() -> dict[str, list[TransactionsExportDay]]:
    return {
        "07-2026": [
            TransactionsExportDay(
                transaction_date="2026-07-12",
                transactions_list=[],
            ),
            TransactionsExportDay(
                transaction_date="2026-07-25",
                transactions_list=[],
            ),
        ],
        "08-2026": [
            TransactionsExportDay(
                transaction_date="2026-08-01",
                transactions_list=[],
            ),
            TransactionsExportDay(
                transaction_date="2026-08-03",
                transactions_list=[],
            ),
        ],
    }


def test_get_split_data(
    export_data: list[TransactionsExportDay],
    result_data: dict[str, list[TransactionsExportDay]],
) -> None:
    result = TransactionsReport.get_split_data(export_data)
    assert result == result_data


def test_get_split_data_empty() -> None:
    result = TransactionsReport.get_split_data([])
    assert result == {}
