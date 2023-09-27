import json
import re
from dataclasses import dataclass, field
from dataclasses import make_dataclass
from typing import List, Optional, Dict
from supersetapiclient.base import Object, default_string, json_field
from supersetapiclient.dashboards.metadataposition import Metadataposition


@dataclass
class Metadata(Object):
    JSON_FIELDS = ['default_filters']

    color_scheme: str = default_string()
    refresh_frequency: int = field(default=0)
    shared_label_colors: Dict = field(default_factory=dict)
    color_scheme_domain: List[str] = field(default_factory=list)
    expanded_slices: Dict = field(default_factory=dict)
    label_colors: Dict = field(default_factory=dict)
    timed_refresh_immune_slices: List[str] = field(default_factory=list)
    cross_filters_enabled: bool = field(default=False)
    filter_scopes: Dict = field(default_factory=dict)
    chart_configuration: Dict = field(default_factory=dict)
    default_filters: dict = json_field()

    def to_dict(self):
        columns = self.field_names()
        return super().to_dict(columns)

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data: dict):
        return super().from_json(data)
