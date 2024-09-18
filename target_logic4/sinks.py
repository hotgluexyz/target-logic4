"""Logic4 target sink class, which handles writing streams."""

import datetime

from target_logic4.client import Logic4Sink


class BuyOrdersSink(Logic4Sink):
    """Qls target sink class."""

    name = "BuyOrders"
    endpoint = "/v1/BuyOrders/CreateBuyOrder"

    def preprocess_record(self, record: dict, context: dict) -> dict:

        created_at = (
            record.get("created_at")
            if record.get("created_at")
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
                "OrderedOnDateByDistributor": record.get("transaction_date")
            }
            if item.get("receipt_date"):
                line_item["ExpectedDeliveryDate"] = item.get("receipt_date")

            PurchaseOrderLines.append(line_item)

        # send only buyorders with lines
        if len(PurchaseOrderLines):
            creditor_id = record.get("supplier_remoteId")
            payload = {
                "CreditorId": int(creditor_id) if creditor_id else None,
                "CreatedAt": created_at,
                "BuyOrderRows": PurchaseOrderLines,
                "Remarks": record.get("remarks")
            }

            if record.get("branch_id"):
                payload["BranchId"] = int(record["branch_id"])

            return payload

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
