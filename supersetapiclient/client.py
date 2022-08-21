"""A Superset REST Api Client."""
import logging
from typing import Union, Tuple, Dict
from functools import partial

import requests
import getpass

from supersetapiclient.dashboards import Dashboards
from supersetapiclient.charts import Charts
from supersetapiclient.datasets import Datasets
from supersetapiclient.databases import Databases
from supersetapiclient.roles import Roles
from supersetapiclient.saved_queries import SavedQueries

logger = logging.getLogger(__name__)


class SupersetClient:
    """A Superset Client."""
    dashboards_cls = Dashboards
    charts_cls = Charts
    datasets_cls = Datasets
    databases_cls = Databases
    saved_queries_cls = SavedQueries
    roles_cls = Roles

    def __init__(
        self,
        host,
        username=None,
        password=None,
        provider="db",
        verify=True,
    ):
        self.host = host
        self.base_url = self.join_urls(host, "/api/v1")
        self.username = getpass.getuser() if username is None else username
        self._password = getpass.getpass() if password is None else password
        self.provider = provider
        self.session = requests.Session()
        self.verify = verify

        self._token, self.refresh_token = self.authenticate()

        # Get CSRF Token
        self._csrf_token = None
        csrf_response = self.session.get(
            self.join_urls(self.base_url, "/security/csrf_token/"),
            headers=self._headers,
            verify=self.verify
        )
        csrf_response.raise_for_status()  # Check CSRF Token went well
        self._csrf_token = csrf_response.json().get("result")

        # Update headers
        self.session.headers.update(
            self._headers
        )

        # Bind method
        self.get = partial(
            self.session.get,
            headers=self._headers,
            verify=self.verify
        )
        self.post = partial(
            self.session.post,
            headers=self._headers,
            verify=self.verify
        )
        self.put = partial(
            self.session.put,
            headers=self._headers,
            verify=self.verify
        )
        self.delete = partial(
            self.session.delete,
            headers=self._headers,
            verify=self.verify
        )

        # Related Objects
        self.dashboards = self.dashboards_cls(self)
        self.charts = self.charts_cls(self)
        self.datasets = self.datasets_cls(self)
        self.databases = self.databases_cls(self)
        self.saved_queries = self.saved_queries_cls(self)
        self.roles = self.roles_cls(self)

    @staticmethod
    def join_urls(*args) -> str:
        """Join multiple urls together.

        Returns:
            str: joined urls
        """
        urls = []
        i = 0
        for u in args:
            i += 1
            if u[0] == "/":
                u = u[1:]
            if u[-1] == "/" and i != len(args):
                u = u[:-1]
            urls.append(u)
        return "/".join(urls)

    def authenticate(self) -> Tuple[str, Union[str, None]]:
        # Try authentication and define session
        response = self.session.post(self.login_endpoint, json={
            "username": self.username,
            "password": self._password,
            "provider": self.provider,
            "refresh": "true"
        }, verify=self.verify)
        response.raise_for_status()
        tokens = response.json()
        return tokens.get("access_token"), tokens.get("refresh_token")

    @property
    def password(self) -> str:
        return "*" * len(self._password)

    @property
    def login_endpoint(self) -> str:
        return self.join_urls(self.base_url, "/security/login")

    @property
    def refresh_endpoint(self) -> str:
        return self.join_urls(self.base_url, "/security/refresh")

    @property
    def token(self) -> str:
        return self._token

    @property
    def csrf_token(self) -> str:
        return self._csrf_token

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "authorization": f"Bearer {self.token}",
            "X-CSRFToken": f"{self.csrf_token}",
            "Referer": f"{self.base_url}"
        }
