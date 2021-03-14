"""A Superset REST Api Client."""
import jwt
from requests import Session


class SupersetClient:
    """A Superset Client."""

    def __init__(
        self,
        host,
        username,
        password,
        port=5000,
    ):
        self.host = host
        self.base_url = self._join_urls(host, "/api/v1")
        self.username = username
        self._password = password
        self.session = Session()

        # Bind method
        self.get = self.session.get
        self.post = self.session.post
        self.put = self.session.put
        self.delete = self.session.delete

        # Try authentication
        response = self.post(self.login_endpoint, json={
            "username": self.username,
            "password": self._password,
            "provider": "db",
            "refresh": "true"
        })
        response.raise_for_status()
        tokens = response.json()
        self._token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")

    def _join_urls(self, *args) -> str:
        """Join multiple urls together.

        Returns:
            str: joined urls
        """
        urls = []
        for u in args:
            if u[0] == "/":
                u = u[1:]
            if u[-1] == "/":
                u = u[:-1]
            urls.append(u)
        return "/".join(urls)

    @property
    def password(self):
        return "*" * len(self._password)

    @property
    def login_endpoint(self):
        return self._join_urls(self.base_url, "/security/login")

    @property
    def refresh_endpoint(self):
        return self._join_urls(self.base_url, "/security/refresh")

    @property
    def token(self):
        return self.token