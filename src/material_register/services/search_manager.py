from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from material_register.controllers.advanced_search_controller import (
        AdvancedSearchController,
    )
    from material_register.controllers.search_controller import SearchController
    from material_register.controllers.transactions_controller import (
        TransactionsController,
    )


class SearchManager:
    _transactions_controller = None
    _search_controller = None
    _advanced_search_controller = None
    _filters_controller = None

    @classmethod
    def setup_controllers(
        cls,
        transactions_controller: "TransactionsController | None" = None,
        search_controller: "SearchController | None" = None,
        advanced_search_controller: "AdvancedSearchController | None" = None,
    ) -> None:
        if transactions_controller is not None:
            cls._transactions_controller = transactions_controller
        if search_controller is not None:
            cls._search_controller = search_controller
        if advanced_search_controller is not None:
            cls._advanced_search_controller = advanced_search_controller

    @classmethod
    def setup_last_controller(cls, controller: str) -> None:
        if controller == cls._advanced_search_controller.__class__.__name__:
            cls._filters_controller = cls._advanced_search_controller
        else:
            cls._filters_controller = cls._search_controller

    @classmethod
    def refresh_filters_data(cls) -> None:
        if cls._filters_controller is not None:
            cls._filters_controller.refresh_filters_data()
