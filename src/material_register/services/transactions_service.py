from PySide6.QtSql import QSqlDatabase

from material_register.db.queries.transaction_items_queries import TransactionItemsQueries
from material_register.db.queries.transactions_queries import TransactionsQueries
from material_register.domain.transaction_item_dataclass import TransactionItem


class TransactionsService:

    @staticmethod
    def insert_new_transaction(db_connection: QSqlDatabase, dialog_data: dict[str, str | int],
                               items_data: list[TransactionItem]) -> tuple[bool, str]:
        try:
            db_connection.transaction()
            transaction_ok, transaction_error, transaction_id = TransactionsQueries.insert_into_transactions(
                db_connection,
                dialog_data["type"],
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
                    item.commodityId,
                    item.unitCount,
                    item.pricePerUnit
                )
                if not ok:
                    db_connection.rollback()
                    return False, item_error
            db_connection.commit()
            return True, ""
        except Exception as e:
            db_connection.rollback()
            return False, str(e)

    @staticmethod
    def update_transaction_with_items(db_connection: QSqlDatabase, transaction_id: int,
                                      dialog_data: dict[str, str | int],
                                      items_data: list[TransactionItem]) -> tuple[bool, str]:
        try:
            db_connection.transaction()
            ok, error = TransactionsQueries.update_transaction(
                db_connection, transaction_id, dialog_data["type"], dialog_data["customer_id"],
                dialog_data["payment_type"], dialog_data["notes"])
            if not ok:
                db_connection.rollback()
                return False, error
            ok, error = TransactionItemsQueries.delete_transaction_items(db_connection, transaction_id)
            if not ok:
                db_connection.rollback()
                return False, error
            for item in items_data:
                ok, error = TransactionItemsQueries.insert_into_transaction_items(
                    db_connection, transaction_id, item.commodityId, item.unitCount, item.pricePerUnit)
                if not ok:
                    db_connection.rollback()
                    return False, error
            db_connection.commit()
            return True, ""
        except Exception as e:
            db_connection.rollback()
            return False, str(e)