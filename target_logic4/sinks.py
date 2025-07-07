"""Logic4 target sink class, which handles writing streams."""

import datetime
from target_logic4.client import Logic4Sink


class BuyOrdersSink(Logic4Sink):
    """Qls target sink class."""

    name = "BuyOrders"
    endpoint = "/v1/BuyOrders/CreateBuyOrder"

    def preprocess_record(self, record: dict, context: dict) -> dict:

        created_at = (
            record.get("transaction_date")
            if record.get("transaction_date")
            else datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        )

        # map lines
        PurchaseOrderLines = []
        line_items = self.parse_objs(record.get("line_items", "[]"))
        for item in line_items:
            product_id = item.get("product_remoteId")
            line_item = {
                "ProductId": int(product_id) if product_id else None,
                "QtyToOrder": item.get("quantity"),
                "QtyToDeliver": item.get("quantity"),
                "ExpectedDeliveryDate": record.get("created_at")
            }
            
            # If  send_OrderedOnDateByDistributor is true or default, add it to payload
            if self._config.get("send_OrderedOnDateByDistributor", True):
                line_item["OrderedOnDateByDistributor"] = created_at
            
            PurchaseOrderLines.append(line_item)

        # send only buyorders with lines
        if len(PurchaseOrderLines):
            creditor_id = record.get("supplier_remoteId")

            # Fetch BranchId from the config file
            branch_id = self._config.get("export_BranchId")

            payload = {
                "CreditorId": int(creditor_id) if creditor_id else None,
                "CreatedAt": created_at,
                "BranchId": int(branch_id) if branch_id else "",  # Use BranchId from config
                "BuyOrderRows": PurchaseOrderLines,
                "Remarks": record.get("remarks")
            }

            return payload

        return dict()

    def upsert_record(self, record: dict, context: dict) -> None:
        """Process the record."""
        state_updates = dict()
        if record:
            self.logger.info(f"Making request to endpoint='{self.endpoint}' with method: 'POST' and payload= {record}")
            response = self.request_api(
                "POST", endpoint=self.endpoint, request_data=record
            )
            self.logger.info(f"Response: {response.text}")
            order_id = response.json().get("Value").get("Id")
            return order_id, True, state_updates
