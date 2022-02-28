"""A Superset REST Api Client."""
import logging
from functools import partial

import requests

from supersetapiclient.dashboards import Dashboards
from supersetapiclient.charts import Charts
from supersetapiclient.datasets import Datasets
from supersetapiclient.databases import Databases

logger = logging.getLogger(__name__)


class SupersetClient:
    """A Superset Client."""

    def __init__(
        self,
        host,
        username,
        password,
        port=8080,
        verify=True,
    ):
        self.host = host
        self.base_url = self.join_urls(host, "/api/v1")
        self.username = username
        self._password = password
        self.session = requests.Session()
        self.verify = verify

        # Try authentication and define session
        response = self.session.post(self.login_endpoint, json={
            "username": self.username,
            "password": self._password,
            "provider": "db",
            "refresh": "true"
        }, verify=self.verify)
        response.raise_for_status()
        tokens = response.json()
        self._token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")

        # Get CSRF Token
        self._csrf_token = None
        csrf_response = self.session.get(
            self.join_urls(self.base_url, "/security/csrf_token"),
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
        self.dashboards = Dashboards(self)
        self.charts = Charts(self)
        self.datasets = Datasets(self)
        self.databases = Databases(self)

    def join_urls(self, *args) -> str:
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
    def _headers(self) -> str:
        return {
            "authorization": f"Bearer {self.token}",
            "X-CSRFToken": f"{self.csrf_token}",
            "Referer": f"{self.base_url}"
        }
