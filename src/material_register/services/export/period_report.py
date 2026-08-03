from material_register.domain.export_dataclass import ExportItemIn, PeriodItemIn


class PeriodReport:

    @staticmethod
    def get_period_data_in(in_data: list[ExportItemIn]) -> dict[str, list[PeriodItemIn]]:
        report_data = {}
        for in_item in in_data:
            if in_item.category_name not in report_data:
                period_item_in = PeriodItemIn(
                    commodity_name=in_item.commodity_name,
                    commodity_unit=in_item.commodity_unit,
                    price_per_unit=in_item.price_per_unit,
                    total_quantity=in_item.total_quantity,
                    total_price=in_item.total_price
                )
                report_data[in_item.category_name] = [period_item_in]
            else:
                items = report_data[in_item.category_name]
                found = False
                for item in items:
                    if item.commodity_name == in_item.commodity_name and item.price_per_unit == in_item.price_per_unit:
                        item.total_quantity += in_item.total_quantity
                        item.total_price += in_item.total_price
                        found = True
                        break
                if not found:
                    period_item_in = PeriodItemIn(
                        commodity_name=in_item.commodity_name,
                        commodity_unit=in_item.commodity_unit,
                        price_per_unit=in_item.price_per_unit,
                        total_quantity=in_item.total_quantity,
                        total_price=in_item.total_price
                    )
                    items.append(period_item_in)
        return report_data