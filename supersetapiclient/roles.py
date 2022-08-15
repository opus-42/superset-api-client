"""Roles."""
from dataclasses import dataclass

from supersetapiclient.base import (
    Object
)


@dataclass
class Role(Object):
    EXPORTABLE = True

    id: int
    name: str
