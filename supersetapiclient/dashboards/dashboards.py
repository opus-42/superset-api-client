"""Dashboards."""
from dataclasses import dataclass, field
from typing import List, Optional

from supersetapiclient.base import Object, ObjectFactories, default_string, json_field
from supersetapiclient.dashboards.metadata import Metadata
from supersetapiclient.dashboards.metadataposition import Metadataposition


@dataclass
class Dashboard(Object):
    JSON_FIELDS = []

    dashboard_title: str
    published: bool
    id: Optional[int] = None
    position_json: dict = json_field()
    changed_by: str = default_string()
    slug: str = default_string()
    changed_by_name: str = default_string()
    changed_by_url: str = default_string()
    css: str = default_string()
    changed_on: str = default_string()
    charts: List[str] = field(default_factory=list)

    metadata: Metadata = Metadata()
    position: Metadataposition = Metadataposition()
    owners: List[int] = field(default_factory=list)
    roles: List[int] = field(default_factory=list)

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

class Dashboards(ObjectFactories):
    endpoint = "dashboard/"
    base_object = Dashboard
