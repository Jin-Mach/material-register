import pytest

from material_register.controllers.customers.customers_filter_helper import CustomersFilterHelper


@pytest.mark.parametrize("text, expected", [
    ("test text",
     "company_normalized LIKE '%test text%' OR first_name_normalized LIKE '%test text%' OR last_name_normalized LIKE '%test text%' OR document_number LIKE '%test text%' OR address_normalized LIKE '%test text%'"),
], ids=["customers filter"])
def test_get_filter(text, expected) -> None:
    result = CustomersFilterHelper.get_filter(text)
    assert "company_normalized LIKE" in result
    assert result.count("OR") == 4