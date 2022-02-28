"""Dashboards."""
from typing import List

from dataclasses import dataclass

from supersetapiclient.base import (
    Object, ObjectFactories, json_field, default_string
)


@dataclass
class Dashboard(Object):
    JSON_FIELDS = [
        "json_metadata",
        "position_json"
    ]
    EXPORTABLE = True

    id: int
    dashboard_title: str
    published: bool
    json_metadata: dict = json_field()
    position_json: dict = json_field()
    changed_by: str = default_string()
    changed_by: str = default_string()
    slug: str = default_string()
    changed_by_name: str = default_string()
    changed_by_url: str = default_string()
    css: str = default_string()
    changed_on: str = default_string()
    charts: list = default_string()

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
        """Get dashboard Slice IDs."""
        charts = []
        for _, v in self.position_json.items():
            if isinstance(v, dict):
                if v.get("type") == "CHART":
                    meta = v.get("meta", {})
                    if meta.get("chartId") is not None:
                        charts.append(meta.get("chartId"))
        return charts


class Dashboards(ObjectFactories):
    endpoint = "/dashboard/"
    base_object = Dashboard
