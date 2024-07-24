import ast
import json
from typing import Dict, List, Optional

from singer_sdk.plugin_base import PluginBase
from target_hotglue.client import HotglueSink

from target_logic4.auth import Logic4Authenticator


class Logic4Sink(HotglueSink):
    def __init__(
        self,
        target: PluginBase,
        stream_name: str,
        schema: Dict,
        key_properties: Optional[List[str]],
    ) -> None:
        """Initialize target sink."""
        self._target = target
        super().__init__(target, stream_name, schema, key_properties)

    base_url = "https://api.logic4server.nl"
    allows_externalid = ["BuyOrders"]

    @property
    def authenticator(self):
        oauth_url = "https://idp.logic4server.nl/token"
        return Logic4Authenticator(self._target, oauth_url)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        headers.update(self.authenticator.auth_headers or {})
        return headers

    def parse_objs(self, obj):
        try:
            return ast.literal_eval(obj)
        except:
            return json.loads(obj)
