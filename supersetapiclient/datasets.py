"""Dashboards."""
from dataclasses import dataclass, field

from supersetapiclient.base import (
    Object, ObjectFactories, json_field, default_string
)


@dataclass
class Dataset(Object):
    JSON_FIELDS = []

    id: int
    table_name: str
    schema: str = ""
    columns: list = field(default_factory=list)
    description: str = ""

class Datasets(ObjectFactories):
    endpoint = "/dataset/"
    base_object = Dataset
