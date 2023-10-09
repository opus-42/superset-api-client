from datetime import datetime
from typing import Any, Literal, Optional, TYPE_CHECKING, Union, Generic, TypeVar

from typing_extensions import NotRequired, TypedDict

T = TypeVar('T')
class NotToJson(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value

FilterValue = Union[bool, datetime, float, int, str]
FilterValues = Union[FilterValue, list[FilterValue], tuple[FilterValue]]

