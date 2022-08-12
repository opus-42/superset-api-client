"""Roles."""
from dataclasses import dataclass

from supersetapiclient.base import (
    Object
)


@dataclass
class Role(Object):
    JSON_FIELDS = []
    LIST_OF_OBJECT_FIELDS = {}
    EXPORTABLE = True

    id: int
    name: str
