"""Charts."""
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
    datasource_type: str = default_string
    viz_type: str = ""
    params: dict = json_field()


class Charts(ObjectFactories):
    endpoint = "/chart/"
    base_object = Chart

    @property
    def add_columns(self):
        # Due to the design of the superset API,
        # get /chart/_info only returns 'slice_name'
        # For chart adds to work,
        # we require the additional attributes:
        #   'datasource_id',
        #   'datasource_type'
        return [
            'datasource_id',
            'datasource_type',
            'slice_name',
            'params',
            'viz_type',
            'description'
        ]
