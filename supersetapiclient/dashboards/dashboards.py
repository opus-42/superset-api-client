"""Dashboards."""
import json
from dataclasses import dataclass, field
from typing import List, Optional
from supersetapiclient.base.base import Object, ObjectFactories, default_string, json_field
from supersetapiclient.dashboards.metadata import Metadata
from supersetapiclient.dashboards.metadataposition import Metadataposition
from supersetapiclient.utils import remove_fields_optional


def defult_metadata():
    return Metadata()

def defult_metadata_position():
    return Metadataposition()


@dataclass
class Dashboard(Object):
    JSON_FIELDS = []

    dashboard_title: str
    published: bool = field(default=False)
    id: Optional[int] = None
    css: str = default_string()
    slug: str = default_string()

    json_metadata: dict = json_field()
    position_json: dict = json_field()

    metadata: Optional[Metadata] = field(default_factory=defult_metadata)
    position: Optional[Metadataposition] = field(default_factory=defult_metadata_position)
    # charts: List[Chart] = field(default_factory=Chart)

    @property
    def colors(self) -> dict:
        """Get dashboard color mapping."""
        return self.json_metadata.get("label_colors", {})

    @colors.setter
    def colors(self, value: dict) -> None:
        """Set dashboard color mapping."""
        self.json_metadata["label_colors"] = value

    def update_colors(self, value: dict) -> None:
        """Update dashboard colors."""
        colors = self.colors
        colors.update(value)
        self.colors = colors

    def get_charts(self) -> List[int]:
        """Get chart objects"""
        charts = []
        for slice_name in self.charts:
            c = self._parent.client.charts.find_one(slice_name=slice_name)
            charts.append(c)
        return charts

    @remove_fields_optional
    def to_dict(self, columns=None):
        data = super().to_dict(columns)
        data['position_json'] = self.position.to_dict()
        data['json_metadata'] = self.metadata.to_dict()
        return data

    @remove_fields_optional
    def to_json(self, columns=None):
        data = super().to_json(columns)
        data['position_json'] = self.position.to_json()
        data['json_metadata'] = self.metadata.to_json()
        return data

    @classmethod
    def from_json(cls, data: dict):
        data_result = data
        if data.get('result'):
            data_result = data['result']
            obj = super().from_json(data_result)
        else:
            obj = super().from_json(data_result)

        obj.metadata = Metadata.from_json(json.loads(data_result['json_metadata']))

        obj.position = Metadata()
        if data_result.get('position_json'):
            obj.position = Metadataposition.from_json(json.loads(data_result['position_json']))
        return obj


class Dashboards(ObjectFactories):
    endpoint = "dashboard/"
    base_object = Dashboard

