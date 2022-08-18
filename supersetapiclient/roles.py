"""Roles."""
from dataclasses import dataclass

from supersetapiclient.base import (
    Object, ObjectFactories
)


@dataclass
class Role(Object):
    JSON_FIELDS = []
    EXPORTABLE = True

    id: int
    name: str


@dataclass
class RoleInfo(Object):
    value: int
    text: str


class Roles(ObjectFactories):
    READ_ONLY = True

    endpoint = "/dashboard/related/roles"
    base_object = RoleInfo
    edit_columns = ['id']

    def create(self, *args) -> Role:
        object = Role(*args)
        object._parent = self
        return object
