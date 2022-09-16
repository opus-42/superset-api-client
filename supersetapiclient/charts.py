"""Charts."""
from dataclasses import dataclass, field
from typing import List, Optional

from supersetapiclient.base import Object, ObjectFactories, default_string, json_field


@dataclass
class Chart(Object):
    JSON_FIELDS = ["params"]

    id: Optional[int] = None
    description: str = default_string()
    slice_name: str = default_string()
    params: dict = json_field()
    datasource_id: Optional[int] = None
    datasource_type: str = default_string()
    viz_type: str = ""
    dashboards: List[int] = field(default_factory=list)

    def to_json(self, columns):
        o = super().to_json(columns)
        o["dashboards"] = self.dashboards
        return o


class Charts(ObjectFactories):
    endpoint = "chart/"
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
            "datasource_id",
            "datasource_type",
            "slice_name",
            "params",
            "viz_type",
            "description",
        ]
