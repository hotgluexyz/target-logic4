"""Logic4 Authentication."""


import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import backoff
import requests
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


class Logic4Authenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for Logic4."""

    def __init__(
        self,
        target,
        auth_endpoint: Optional[str] = None,
    ) -> None:
        """Init authenticator.

        Args:
            stream: A stream for a RESTful endpoint.
        """
        self.target_name: str = target.name
        self._config: Dict[str, Any] = target._config
        self._auth_headers: Dict[str, Any] = {}
        self._auth_params: Dict[str, Any] = {}
        self.logger: logging.Logger = target.logger
        self._auth_endpoint = auth_endpoint
        self._config_file = target.config_file
        self._target = target

    @property
    def auth_headers(self) -> dict:
        headers = {}
        if not self.is_token_valid():
            self.update_access_token()
        headers["Authorization"] = f"Bearer {self.config.get('access_token')}"
        return headers

    def is_token_valid(self) -> bool:
        access_token = self._config.get("access_token")
        now = round(datetime.utcnow().timestamp())
        expires_in = self.config.get("expires_in")
        if expires_in is not None:
            expires_in = int(expires_in)
        if not access_token:
            return False

        if not expires_in:
            return False

        return not ((expires_in - now) < 120)

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the Logic4 API."""
        # build scope
        scope = self.config.get("scope", "api administration.1")
        if not scope.startswith("api"):
            scope = f"api {scope}"

        return {
            "grant_type": "client_credentials",
            "client_id": f"{self.config['public_key']} {self.config['company_key']} {self.config['username']}",
            "client_secret": f"{self.config['secret_key']} {self.config['password']}",
            "scope": scope,
        }

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def update_access_token(self) -> None:
        self.logger.info(
            f"Oauth request - endpoint: {self._auth_endpoint}, body: {self.oauth_request_body}"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_response = requests.post(
            self._auth_endpoint, data=self.oauth_request_body, headers=headers
        )
        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.text}'. {ex}"
            )
        token_json = token_response.json()
        # Log the refresh_token
        self._config["access_token"] = token_json["access_token"]
        now = round(datetime.utcnow().timestamp())
        self._config["expires_in"] = now + token_json["expires_in"]

        with open(self._target.config_file, "w") as outfile:
            json.dump(self._config, outfile, indent=4)
