from material_register.services import db_cache
from material_register.domain.customers_dataclass import Customer


def test_filter_active_customers_picks_active():
    active_customer = Customer(document_number="1", address="x", active=1)
    inactive_customer = Customer(document_number="2", address="y", active=0)
    db_cache.DbCache.customers = [active_customer, inactive_customer]
    result = db_cache.DbCache._filter_active_customers()
    assert result == [active_customer]

def test_filter_inactive_customers_picks_inactive():
    active_customer = Customer(document_number="1", address="x", active=1)
    inactive_customer = Customer(document_number="2", address="y", active=0)
    db_cache.DbCache.customers = [active_customer, inactive_customer]
    result = db_cache.DbCache._filter_inactive_customers()
    assert result == [inactive_customer]