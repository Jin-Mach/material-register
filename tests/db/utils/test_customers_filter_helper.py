from material_register.db.utils.customers_filter_helper import CustomersFilterHelper


def test_get_filter() -> None:
    result = CustomersFilterHelper.get_filter("test text")
    assert "company_normalized LIKE" in result
    assert result.count("OR") == 4
