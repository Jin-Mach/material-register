from PySide6.QtSql import QSqlDatabase

from material_register.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.db.queries.inventory_queries import InventoryQueries
from material_register.db.queries.transaction_items_queries import (
    TransactionItemsQueries,
)
from material_register.db.queries.transactions_queries import TransactionsQueries
from material_register.domain.transaction_item_dataclass import TransactionItem


class TransactionsService:

    @staticmethod
    def create_transaction(db_connection: QSqlDatabase, dialog_data: dict[str, str | int],
                           items_data: list[TransactionItem]) -> tuple[bool, str]:
        try:
            db_connection.transaction()
            transaction_ok, transaction_error, transaction_id = TransactionsQueries.insert_into_transactions(
                db_connection,
                dialog_data["transaction_type"],
                dialog_data["customer_id"],
                dialog_data["payment_type"],
                dialog_data["notes"]
            )
            if not transaction_ok:
                db_connection.rollback()
                return False, transaction_error
            if transaction_id is None:
                db_connection.rollback()
                return False, "Missing transaction id"
            for item in items_data:
                ok, item_error = TransactionItemsQueries.insert_into_transaction_items(
                    db_connection,
                    transaction_id,
                    item.commodity_id,
                    item.unit_count,
                    item.price_per_unit
                )
                if not ok:
                    db_connection.rollback()
                    return False, item_error
                transfer_type = dialog_data["transaction_type"]
                if transfer_type not in (TRANSFER_IN, TRANSFER_OUT):
                    db_connection.rollback()
                    return False, "Invalid transfer type"
                amount = TransactionsService._get_amount(transfer_type, item.unit_count)
                ok, inventory_error = InventoryQueries.update_inventory_item(db_connection, item.commodity_id, amount)
                if not ok:
                    db_connection.rollback()
                    return False, inventory_error
            db_connection.commit()
            return True, ""
        except Exception as e:
            db_connection.rollback()
            return False, str(e)

    @staticmethod
    def update_transaction(db_connection: QSqlDatabase, transaction_id: int,
                           dialog_data: dict[str, str | int],
                           new_items_data: list[TransactionItem],
                           old_items_data: list[TransactionItem]) -> tuple[bool, str, bool]:
        try:
            db_connection.transaction()
            new_stock_dict = TransactionsService._get_stock_dict(new_items_data)
            old_stock_dict = TransactionsService._get_stock_dict(old_items_data)
            final_stock_dict = TransactionsService._get_final_stock_dict(old_stock_dict, new_stock_dict,
                                                                         dialog_data["transaction_type"])
            items_changed = old_items_data != new_items_data
            if not final_stock_dict and not items_changed:
                return True, "", False
            ok, error = TransactionsQueries.update_transaction(
                db_connection, transaction_id, dialog_data["transaction_type"], dialog_data["customer_id"],
                dialog_data["payment_type"], dialog_data["notes"])
            if not ok:
                db_connection.rollback()
                return False, error, False
            ok, error = TransactionItemsQueries.delete_transaction_items(db_connection, transaction_id)
            if not ok:
                db_connection.rollback()
                return False, error, False
            for item in new_items_data:
                ok, error = TransactionItemsQueries.insert_into_transaction_items(
                    db_connection, transaction_id, item.commodity_id, item.unit_count, item.price_per_unit)
                if not ok:
                    db_connection.rollback()
                    return False, error, False
            for commodity_id, amount in final_stock_dict.items():
                ok, inventory_error = InventoryQueries.update_inventory_item(db_connection, commodity_id, amount)
                if not ok:
                    db_connection.rollback()
                    return False, inventory_error, False
            db_connection.commit()
            return True, "", True
        except Exception as e:
            db_connection.rollback()
            return False, str(e), False

    @staticmethod
    def delete_transaction(db_connection: QSqlDatabase, transaction_id: int, transfer_type: str) -> tuple[bool, str]:
        try:
            db_connection.transaction()
            items = TransactionItemsQueries.get_transaction_items(db_connection, transaction_id)
            for item in items:
                amount = TransactionsService._get_amount(transfer_type, item.unit_count, negate=True)
                ok, error = InventoryQueries.update_inventory_item(db_connection, item.commodity_id, amount)
                if not ok:
                    db_connection.rollback()
                    return False, error
            ok, error = TransactionsQueries.delete_transaction(db_connection, transaction_id)
            if not ok:
                db_connection.rollback()
                return False, error
            db_connection.commit()
            return True, ""
        except Exception as e:
            db_connection.rollback()
            return False, str(e)

    @staticmethod
    def _get_amount(transfer_type: str, amount: float, negate: bool = False) -> int | float:
        operator = 1
        if transfer_type == TRANSFER_OUT:
            operator = -1
        if negate:
            operator = -operator
        return operator * amount

    @staticmethod
    def _get_stock_dict(items_list: list[TransactionItem]) -> dict[int, float]:
        stock_dict = {}
        for item in items_list:
            if item.commodity_id not in stock_dict:
                stock_dict[item.commodity_id] = item.unit_count
            else:
                stock_dict[item.commodity_id] += item.unit_count
        return stock_dict

    @staticmethod
    def _get_final_stock_dict(old_items: dict[int, float], new_items: dict[int, float],
                              transfer_type: str) -> dict[int, float]:
        final_stock_dict = {}
        all_ids = set(old_items) | set(new_items)
        for commodity_id in all_ids:
            old_amount = old_items.get(commodity_id, 0)
            new_amount = new_items.get(commodity_id, 0)
            amount = TransactionsService._get_amount(transfer_type, new_amount - old_amount)
            if amount != 0:
                final_stock_dict[commodity_id] = amount
        return final_stock_dict