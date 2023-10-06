"""Custom Exception."""
import json
import traceback

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


class ItemPositionValidationError(Exception):
    pass


class AcceptChildError(Exception):
    def __init__(self, message='Item position does not allow including children'):
        super().__init__(message)


class LoadJsonError(Exception):
    pass


class NodePositionValidationError(Exception):
    pass


class DashboardValidationError(Exception):
    pass

class ChartValidationError(Exception):
    pass