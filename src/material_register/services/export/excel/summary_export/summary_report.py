from material_register.domain.export_dataclass.summary_dataclass import (
    SummaryExportItemIn,
    SummaryExportItemOut,
    SummaryItemDataIn,
    SummaryItemDataOut,
)


class SummaryReport:
    @staticmethod
    def get_summary_data_in(
        in_data: list[SummaryExportItemIn],
    ) -> dict[str, list[SummaryItemDataIn]]:
        report_data = {}
        for in_item in in_data:
            if in_item.category_name not in report_data:
                summary_item_in = SummaryItemDataIn(
                    commodity_name=in_item.commodity_name,
                    commodity_unit=in_item.commodity_unit,
                    price_per_unit=in_item.price_per_unit,
                    total_quantity=in_item.total_quantity,
                    total_price=in_item.total_price,
                )
                report_data[in_item.category_name] = [summary_item_in]
            else:
                items = report_data[in_item.category_name]
                found = False
                for item in items:
                    if (
                        item.commodity_name == in_item.commodity_name
                        and item.price_per_unit == in_item.price_per_unit
                    ):
                        item.total_quantity += in_item.total_quantity
                        item.total_price += in_item.total_price
                        found = True
                        break
                if not found:
                    summary_item_in = SummaryItemDataIn(
                        commodity_name=in_item.commodity_name,
                        commodity_unit=in_item.commodity_unit,
                        price_per_unit=in_item.price_per_unit,
                        total_quantity=in_item.total_quantity,
                        total_price=in_item.total_price,
                    )
                    items.append(summary_item_in)
        return report_data

    @staticmethod
    def get_summary_data_out(
        out_data: list[SummaryExportItemOut],
    ) -> dict[str, list[SummaryItemDataOut]]:
        report_data = {}
        for out_item in out_data:
            summary_item_out = SummaryItemDataOut(
                commodity_name=out_item.commodity_name,
                commodity_unit=out_item.commodity_unit,
                total_quantity=out_item.total_quantity,
            )
            if out_item.category_name not in report_data:
                report_data[out_item.category_name] = []
            report_data[out_item.category_name].append(summary_item_out)
        return report_data
