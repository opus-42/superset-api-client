"""A Superset REST Api Client."""
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
        self.username = username
        self._password = password
        self.session = Session()

        # Bind method
        self.get = self.session.get
        self.post = self.session.post
        self.put = self.session.put
        self.delete = self.session.delete


    @property
    def password(self):
        return "*" * len(self._password)
