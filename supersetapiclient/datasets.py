"""Dashboards."""
from dataclasses import dataclass, field

from supersetapiclient.base import (
    Object, ObjectFactories
)


@dataclass
class Dataset(Object):
    JSON_FIELDS = []
    EXPORTABLE = True

    id: int
    table_name: str
    schema: str = ""
    columns: list = field(default_factory=list)
    description: str = ""


class Datasets(ObjectFactories):
    endpoint = "/dataset/"
    base_object = Dataset
