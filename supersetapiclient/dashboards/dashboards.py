"""Dashboards."""
import json
from dataclasses import dataclass, field
from typing import List, Optional
from supersetapiclient.base.base import Object, ObjectFactories, default_string, json_field
from supersetapiclient.dashboards.itemposition import ItemPosition
from supersetapiclient.dashboards.metadata import Metadata
from supersetapiclient.dashboards.metadataposition import Metadataposition
from supersetapiclient.dashboards.nodeposisition import RowNodePosition
from supersetapiclient.exceptions import DashboardValidationError
from supersetapiclient.typing import NotToJson


def defult_metadata():
    return Metadata()

def defult_metadata_position():
    return Metadataposition()


@dataclass
class Dashboard(Object):
    JSON_FIELDS = ['json_metadata', 'position_json']

    dashboard_title: str
    published: bool = field(default=False)
    id: NotToJson[int] = None
    css: str = default_string()
    slug: str = None

    json_metadata: Metadata = field(default_factory=Metadata)
    position_json: Metadataposition = field(default_factory=Metadataposition)
    # charts: List[Chart] = field(default_factory=Chart)

    @property
    def metadata(self):
        return self.json_metadata

    @property
    def position(self):
        return self.position_json

    def add_chart(self, chart, title:str, parent: ItemPosition=None):
        chart.add_dashboard(self)
        if not self.id:
            raise DashboardValidationError('To add charts, first save the dashboard. Do this by calling the client.dashboards.add([this-dashboard]) method.')
        if not chart.id:
            self._factory.client.charts.add(chart, title, update_dashboard=False)

        self._factory.client.charts.add_to_dashboard(chart, self.id)

        self.metadata.add_chart(chart)

        node_position = parent
        if node_position is None:
            if not node_position:
                grid = self.position.tree.grid
                node_position = grid
                if grid.children:
                    node_position = grid.children[-1]
                if not isinstance(node_position, RowNodePosition):
                    node_position = grid
        self.position.add_chart(chart, title, node_position)


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
        #http://localhost:8088/api/v1/dashboard/21/charts
        charts = []
        for slice_name in self.charts:
            c = self._factory.client.charts.find_one(slice_name=slice_name)
            charts.append(c)
        return charts

    def get_datasets(self):
        pass
        #http://localhost:8088/api/v1/dashboard/21/datasets


class Dashboards(ObjectFactories):
    endpoint = "dashboard/"
    base_object = Dashboard