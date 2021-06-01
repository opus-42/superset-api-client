"""Dashboards."""
from dataclasses import dataclass

from supersetapiclient.base import (
    Object, ObjectFactories, json_field, default_string
)


@dataclass
class Dataset(Object):
    JSON_FIELDS = []

    id: int
    description: default_string()
    table_name: default_string()
    columns: json_field()


class Datasets(ObjectFactories):
    endpoint = "/dataset/"
    base_object = Dataset
