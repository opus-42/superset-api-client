"""Roles."""
from dataclasses import dataclass

from supersetapiclient.base import (
    Object
)


@dataclass
class Role(Object):
    JSON_FIELDS = []
    EXPORTABLE = True

    id: int
    name: str
