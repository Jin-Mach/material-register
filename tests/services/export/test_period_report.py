import pytest

from material_register.domain.export_dataclass import PeriodItemIn, ExportItemIn
from material_register.services.export.period_report import PeriodReport


@pytest.fixture
def export_data_in() -> list[ExportItemIn]:
    return [
        ExportItemIn(category_name="FE", commodity_name="12345", commodity_unit="kg",
                     price_per_unit=0.8, total_quantity=100.0, total_price=80.0
                     ),
        ExportItemIn(category_name="FE", commodity_name="12345", commodity_unit="kg",
                     price_per_unit=0.8, total_quantity=50.0, total_price=40.0),
        ExportItemIn(category_name="FE", commodity_name="12345", commodity_unit="kg",
                     price_per_unit=1.8, total_quantity=20.0, total_price=36.0),
        ExportItemIn(category_name="FE", commodity_name="67890", commodity_unit="kg",
                     price_per_unit=7.9, total_quantity=10.0, total_price=79.0),
        ExportItemIn(category_name="CU", commodity_name="54321", commodity_unit="kg",
                     price_per_unit=23.5, total_quantity=5.0, total_price=117.5
                     )
    ]

@pytest.fixture
def result_data_in() -> dict[str, list[PeriodItemIn]]:
    return {
        "FE": [PeriodItemIn(commodity_name="12345", commodity_unit="kg",
                            price_per_unit=0.8, total_quantity=150.0, total_price=120.0),
               PeriodItemIn(commodity_name="12345", commodity_unit="kg",
                            price_per_unit=1.8, total_quantity=20.0, total_price=36.0),
               PeriodItemIn(commodity_name="67890", commodity_unit="kg",
                            price_per_unit=7.9, total_quantity=10.0, total_price=79.0)
               ],
        "CU": [PeriodItemIn(commodity_name="54321", commodity_unit="kg",
                            price_per_unit=23.5, total_quantity=5.0, total_price=117.5)
        ]
    }

def test_get_period_data_in(export_data_in: list[ExportItemIn], result_data_in: dict[str, list[PeriodItemIn]]) -> None:
    result = PeriodReport.get_period_data_in(export_data_in)
    assert result == result_data_in

def test_get_period_data_in_empty() -> None:
    result = PeriodReport.get_period_data_in([])
    assert result == {}