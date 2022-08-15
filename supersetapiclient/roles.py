"""Roles."""
from dataclasses import dataclass

from supersetapiclient.base import (
    Object
)


@dataclass
class Role(Object):

    id: int
    name: str
