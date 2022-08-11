"""Custom Exception."""
from requests import HTTPError


class NotFound(Exception):
    pass


class QueryLimitReached(Exception):
    pass


class ServerError(HTTPError):
    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop("message", None)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.message
