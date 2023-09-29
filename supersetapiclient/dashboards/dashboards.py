"""Dashboards."""
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from supersetapiclient.base import Object, ObjectFactories, default_string, json_field, default_bool
from supersetapiclient.dashboards.metadata import Metadata
from supersetapiclient.dashboards.metadataposition import Metadataposition


@dataclass
class Dashboard(Object):
    JSON_FIELDS = ['native_filter_configuration']

    dashboard_title: str
    published: bool
    id: Optional[int] = None
    certification_details: str = default_string()
    certified_by: str = default_string()
    created_by: str = default_string()
    created_on_delta_humanized: str = default_string()
    changed_by: str = default_string()
    changed_by_name: str = default_string()
    changed_by_url: str = default_string()
    changed_on: str = default_string()
    changed_on_delta_humanized: str = default_string()
    changed_on_utc: str = default_string()
    charts: List[str] = field(default_factory=list)
    css: str = default_string()
    is_managed_externally: bool = default_bool()
    native_filter_configuration: dict = json_field()
    slug: str = default_string()
    status: str = default_string()
    tags: List[str] = field(default_factory=list)
    owners: List[int] = field(default_factory=list)
    roles: List[int] = field(default_factory=list)
    thumbnail_url: str = default_string()
    url: str = default_string()

    json_metadata: dict = json_field()
    position_json: dict = json_field()
    metadata: Metadata = field(default_factory=Metadata)
    position: Metadataposition = field(default_factory=Metadataposition)


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

    def to_json(self, columns=None):
        if columns is None:
            columns = self.field_names()
        data = super().to_json(columns)
        data['position_json'] = self.position.to_json()
        data['json_metadata'] = self.metadata.to_json()
        return data

    @classmethod
    def from_json(cls, data: dict):
        print(data)
        obj = super().from_json(data)
        obj.metadata = Metadata.from_json(json.loads(data['json_metadata']))
        obj.position = Metadataposition.from_json(json.loads(data['position_json']))
        return obj

class Dashboards(ObjectFactories):
    endpoint = "dashboard/"
    base_object = Dashboard
