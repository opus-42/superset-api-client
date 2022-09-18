"""Custom Exception."""
import json

from requests import HTTPError


class NotFound(Exception):
    pass


class MultipleFound(Exception):
    pass


class QueryLimitReached(Exception):
    pass


class BadRequestError(HTTPError):
    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop("message", None)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return json.dumps(self.message, indent=4)


class ComplexBadRequestError(HTTPError):
    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop("errors", None)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return json.dumps(self.errors, indent=4)
