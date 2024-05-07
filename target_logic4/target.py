"""Logic4 target class."""

from pathlib import PurePath
from typing import List, Optional, Union

from singer_sdk import typing as th
from target_hotglue.target import TargetHotglue

from target_logic4.sinks import BuyOrdersSink


class TargetLogic4(TargetHotglue):
    """Sample target for Logic4."""

    def __init__(
        self,
        config: Optional[Union[dict, PurePath, str, List[Union[PurePath, str]]]] = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
        state: str = None,
    ) -> None:
        self.config_file = config[0]
        super().__init__(config, parse_env_config, validate_config)

    name = "target-logic4"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "public_key",
            th.StringType,
            required=True,
        ),
        th.Property(
            "company_key",
            th.StringType,
            required=True,
        ),
        th.Property(
            "username",
            th.StringType,
            required=True,
        ),
        th.Property(
            "secret_key",
            th.StringType,
            required=True,
        ),
        th.Property(
            "password",
            th.StringType,
            required=True,
        ),
        th.Property(
            "scope",
            th.StringType,
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
        ),
    ).to_dict()

    SINK_TYPES = [BuyOrdersSink]


if __name__ == "__main__":
    TargetLogic4.cli()
