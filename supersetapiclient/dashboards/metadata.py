import json
from dataclasses import dataclass, field
from typing import List, Dict
from supersetapiclient.base.base import Object, default_string, json_field


@dataclass
class Metadata(Object):
    JSON_FIELDS = []

    color_scheme: str = default_string()
    refresh_frequency: int = field(default=0)
    shared_label_colors: Dict = field(default_factory=dict)
    color_scheme_domain: List[str] = field(default_factory=list)
    expanded_slices: Dict = field(default_factory=dict)
    label_colors: Dict = field(default_factory=dict)
    timed_refresh_immune_slices: List[str] = field(default_factory=list)
    cross_filters_enabled: bool = field(default=False)
    # filter_scopes: Dict = field(default_factory=dict)
    chart_configuration: Dict = field(default_factory=dict)
    global_chart_configuration: Dict = field(default_factory=dict)
    default_filters: Dict = field(default_factory=dict)

    def to_dict(self, columns=None):
        data = super().to_dict(columns)
        # breakpoint()
        # data['shared_label_colors']
        return data

    def to_json(self, columns=None):
        data = super().to_json(columns)
        if isinstance(data['default_filters'], dict):
            data['default_filters'] = json.dumps(data['default_filters'])

        return json.dumps(data)

    @classmethod
    def from_json(cls, data: dict):
        return super().from_json(data)
