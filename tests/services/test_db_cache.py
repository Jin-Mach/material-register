from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.domain.customers_dataclass import Customer
from material_register.services import db_cache


def test_refresh_customers_data_preserves_cache_on_query_error(monkeypatch) -> None:
    customer = Customer(document_number="1", address="x", active=1)
    monkeypatch.setattr(db_cache.DbCache, "customers", [customer])
    monkeypatch.setattr(db_cache.DbCache, "active_customers", [customer])
    monkeypatch.setattr(db_cache.DbCache, "inactive_customers", [])
    monkeypatch.setattr(
        db_cache.CustomersQueries,
        "get_customers",
        lambda connection: (False, "customer query failed", []),
    )
    ok, error = db_cache.DbCache.refresh_customers_data()
    assert ok is False
    assert error == "customer query failed"
    assert db_cache.DbCache.customers == [customer]
    assert db_cache.DbCache.active_customers == [customer]
    assert db_cache.DbCache.inactive_customers == []


def test_refresh_customers_data_accepts_successful_empty_results(monkeypatch) -> None:
    monkeypatch.setattr(
        db_cache.CustomersQueries,
        "get_customers",
        lambda connection: (True, "", []),
    )
    ok, error = db_cache.DbCache.refresh_customers_data()
    assert ok is True
    assert error == ""
    assert db_cache.DbCache.customers == []
    assert db_cache.DbCache.active_customers == []
    assert db_cache.DbCache.inactive_customers == []


def test_refresh_catalog_data_preserves_cache_on_query_error(monkeypatch) -> None:
    categories = [Category(id=1, name="old", notes="")]
    commodities = [
        Commodity(
            id=1,
            name="old",
            category_id=1,
            unit="pcs",
            default_price=1,
            notes="",
            active=1,
        )
    ]
    monkeypatch.setattr(db_cache.DbCache, "categories", categories)
    monkeypatch.setattr(db_cache.DbCache, "commodities", commodities)
    monkeypatch.setattr(
        db_cache.CategoryQueries,
        "get_categories",
        lambda connection: (True, "", [Category(id=2, name="new", notes="")]),
    )
    monkeypatch.setattr(
        db_cache.CommoditiesQueries,
        "get_commodities",
        lambda connection: (False, "commodity query failed", []),
    )
    ok, error = db_cache.DbCache.refresh_catalog_data()
    assert ok is False
    assert error == "commodity query failed"
    assert db_cache.DbCache.categories == categories
    assert db_cache.DbCache.commodities == commodities


def test_refresh_catalog_data_accepts_successful_empty_results(monkeypatch) -> None:
    monkeypatch.setattr(
        db_cache.CategoryQueries,
        "get_categories",
        lambda connection: (True, "", []),
    )
    monkeypatch.setattr(
        db_cache.CommoditiesQueries,
        "get_commodities",
        lambda connection: (True, "", []),
    )
    ok, error = db_cache.DbCache.refresh_catalog_data()
    assert ok is True
    assert error == ""
    assert db_cache.DbCache.categories == []
    assert db_cache.DbCache.commodities == []


def test_filter_active_customers_picks_active() -> None:
    active_customer = Customer(document_number="1", address="x", active=1)
    inactive_customer = Customer(document_number="2", address="y", active=0)
    db_cache.DbCache.customers = [active_customer, inactive_customer]
    result = db_cache.DbCache._filter_active_customers()
    assert result == [active_customer]


def test_filter_inactive_customers_picks_inactive() -> None:
    active_customer = Customer(document_number="1", address="x", active=1)
    inactive_customer = Customer(document_number="2", address="y", active=0)
    db_cache.DbCache.customers = [active_customer, inactive_customer]
    result = db_cache.DbCache._filter_inactive_customers()
    assert result == [inactive_customer]
