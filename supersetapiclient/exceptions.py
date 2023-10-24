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


class ValidationError(Exception):
    def __init__(self, message:str, solution:str = 'There is not.'):
        # from django.core.exceptions import ValidationError
        super().__init__(message, solution)
        self.message = message
        self.solution = solution

class NodePositionValidationError(ValidationError):
    def __init__(self, message:str, solution:str = None):
        super().__init__(message, solution)


class DashboardValidationError(ValidationError):
    def __init__(self, message:str, solution:str = None):
        super().__init__(message, solution)


class ChartValidationError(ValidationError):
    def __init__(self, message:str, solution:str = None):
        super().__init__(message, solution)