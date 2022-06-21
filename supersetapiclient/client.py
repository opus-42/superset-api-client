"""A Superset REST Api Client."""
import logging
from functools import partial

import requests_oauthlib

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
        provider="db",
        verify=True,
    ):
        self.host = host
        self.base_url = self.join_urls(host, "/api/v1")
        self.username = username
        self._password = password
        self.provider = provider
        self.verify = verify

        token = self.authenticate()
        self.session = requests_oauthlib.OAuth2Session(token=token)
        self.session.hooks['response'] = [self.token_refresher]

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

    def authenticate(self) -> dict:
        # Try authentication and define session
        response = self.session.post(self.login_endpoint, json={
            "username": self.username,
            "password": self._password,
            "provider": self.provider,
            "refresh": "true"
        }, verify=self.verify)
        response.raise_for_status()
        return response.json()

    def token_refresher(self, r, *args, **kwargs):
        """A requests response hook that refreshes the access token if needed"""
        if r.status_code == 401:
            refresh_token = self.session.token["refresh_token"]
            tmp_token = {"access_token": refresh_token}
            # Create a new session to avoid messing up the current session
            refresh_r = requests_oauthlib.OAuth2Session(token=tmp_token).post(self.refresh_endpoint)
            refresh_r.raise_for_status()
            new_token = refresh_r.json()
            if "refresh_token" not in new_token:
                new_token["refresh_token"] = refresh_token
            self.session.token = new_token
            r.request.headers["Authorization"] = f"Bearer {new_token['access_token']}"
            return self.session.send(r.request, verify=False)

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
    def csrf_token(self) -> str:
        return self._csrf_token

    @property
    def _headers(self) -> dict:
        return {
            "X-CSRFToken": f"{self.csrf_token}",
            "Referer": f"{self.base_url}"
        }
