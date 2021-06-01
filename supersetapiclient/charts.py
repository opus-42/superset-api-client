"""Dashboards."""
from typing import List

from dataclasses import dataclass

from supersetapiclient.base import (
    Object, ObjectFactories, json_field, default_string
)


@dataclass
class Chart(Object):
    JSON_FIELDS = [
        "params"
    ]

    id: int
    description: default_string()
    slice_name: default_string()
    params: json_field()
    datasource_id: int = None
    viz_type: str = ""


class Charts(ObjectFactories):
    endpoint = "/chart/"
    base_object = Chart
