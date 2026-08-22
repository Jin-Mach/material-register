import pytest

from material_register.domain.export_dataclass.summary_dataclass import (
    SummaryExportItemIn,
    SummaryExportItemOut,
    SummaryItemDataIn,
    SummaryItemDataOut,
)
from material_register.services.export.summary_report import SummaryReport


@pytest.fixture
def export_data_in() -> list[SummaryExportItemIn]:
    return [
        SummaryExportItemIn(
            category_name="A",
            commodity_name="12345",
            commodity_unit="kg",
            price_per_unit=0.8,
            total_quantity=100.0,
            total_price=80.0,
        ),
        SummaryExportItemIn(
            category_name="A",
            commodity_name="12345",
            commodity_unit="kg",
            price_per_unit=0.8,
            total_quantity=50.0,
            total_price=40.0,
        ),
        SummaryExportItemIn(
            category_name="A",
            commodity_name="12345",
            commodity_unit="kg",
            price_per_unit=1.8,
            total_quantity=20.0,
            total_price=36.0,
        ),
        SummaryExportItemIn(
            category_name="A",
            commodity_name="67890",
            commodity_unit="kg",
            price_per_unit=7.9,
            total_quantity=10.0,
            total_price=79.0,
        ),
        SummaryExportItemIn(
            category_name="B",
            commodity_name="54321",
            commodity_unit="kg",
            price_per_unit=23.5,
            total_quantity=5.0,
            total_price=117.5,
        ),
    ]


@pytest.fixture
def result_data_in() -> dict[str, list[SummaryItemDataIn]]:
    return {
        "A": [
            SummaryItemDataIn(
                commodity_name="12345",
                commodity_unit="kg",
                price_per_unit=0.8,
                total_quantity=150.0,
                total_price=120.0,
            ),
            SummaryItemDataIn(
                commodity_name="12345",
                commodity_unit="kg",
                price_per_unit=1.8,
                total_quantity=20.0,
                total_price=36.0,
            ),
            SummaryItemDataIn(
                commodity_name="67890",
                commodity_unit="kg",
                price_per_unit=7.9,
                total_quantity=10.0,
                total_price=79.0,
            ),
        ],
        "B": [
            SummaryItemDataIn(
                commodity_name="54321",
                commodity_unit="kg",
                price_per_unit=23.5,
                total_quantity=5.0,
                total_price=117.5,
            )
        ],
    }


@pytest.fixture
def export_data_out() -> list[SummaryExportItemOut]:
    return [
        SummaryExportItemOut(
            category_name="A",
            commodity_name="12345",
            commodity_unit="kg",
            total_quantity=600.0,
        ),
        SummaryExportItemOut(
            category_name="A",
            commodity_name="67890",
            commodity_unit="kg",
            total_quantity=100.0,
        ),
        SummaryExportItemOut(
            category_name="B",
            commodity_name="54321",
            commodity_unit="kg",
            total_quantity=100.0,
        ),
    ]


@pytest.fixture
def result_data_out() -> dict[str, list[SummaryItemDataOut]]:
    return {
        "A": [
            SummaryItemDataOut(
                commodity_name="12345",
                commodity_unit="kg",
                total_quantity=600.0,
            ),
            SummaryItemDataOut(
                commodity_name="67890",
                commodity_unit="kg",
                total_quantity=100.0,
            ),
        ],
        "B": [
            SummaryItemDataOut(
                commodity_name="54321",
                commodity_unit="kg",
                total_quantity=100.0,
            )
        ],
    }


def test_get_summary_data_in(
    export_data_in: list[SummaryExportItemIn],
    result_data_in: dict[str, list[SummaryItemDataIn]],
) -> None:
    result = SummaryReport.get_summary_data_in(export_data_in)
    assert result == result_data_in


def test_get_summary_data_in_empty() -> None:
    result = SummaryReport.get_summary_data_in([])
    assert result == {}


def test_get_summary_data_out(
    export_data_out: list[SummaryExportItemOut],
    result_data_out: dict[str, list[SummaryItemDataOut]],
) -> None:
    result = SummaryReport.get_summary_data_out(export_data_out)
    assert result == result_data_out


def test_get_summary_data_out_empty() -> None:
    result = SummaryReport.get_summary_data_out([])
    assert result == {}
