import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from supersetapiclient.base import Object, default_string, json_field
from supersetapiclient.dashboards.metadataposition import Metadataposition


@dataclass
class Metadata(Object):
    JSON_FIELDS = ['default_filters']

    color_scheme: str = default_string()
    # positions: dict = json_field()
    position: Metadataposition = Metadataposition()
    refresh_frequency: int = field(default=0)
    shared_label_colors: dict = field(default_factory=dict)
    color_scheme_domain: List[str] = field(default_factory=list)
    expanded_slices: dict = field(default_factory=dict)
    label_colors: dict = field(default_factory=dict)
    timed_refresh_immune_slices: List[str] = field(default_factory=list)
    cross_filters_enabled: bool = field(default=False)
    filter_scopes: dict = field(default_factory=dict)
    chart_configuration: dict = field(default_factory=dict)
    default_filters: dict = json_field()

    def to_json(self, columns=None):
        if columns is None:
            columns = self.field_names()
        data = super().to_json(columns)
        data['positions'] = self.position.to_json()
        return json.dumps(data)