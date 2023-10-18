import json
from dataclasses import dataclass, field
from typing import List, Dict
from supersetapiclient.base.base import Object, default_string, ObjectField
from supersetapiclient.typing import Optional


@dataclass
class CrossFilters(Object):
    scope: str = 'global'
    chartsInScope: List[int] = field(default_factory=list)


@dataclass
class ChartConfiguration(Object):
    id: int
    crossFilters: CrossFilters = ObjectField(cls=ObjectField, default_factory=ObjectField)


@dataclass
class GlobalChartconfigurationScope(Object):
    rootPath: List[str] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)


@dataclass
class GlobalChartconfiguration(Object):
    scope : GlobalChartconfigurationScope = ObjectField(cls=GlobalChartconfigurationScope, default_factory=GlobalChartconfigurationScope)
    chartsInScope: List[str] = field(default_factory=list)


@dataclass
class Metadata(Object):
    JSON_FIELDS = ['default_filters']

    color_scheme: str = default_string()
    refresh_frequency: int = field(default=0)
    shared_label_colors: Dict[str,str] = field(default_factory=dict)
    color_scheme_domain: List[str] = field(default_factory=list)
    expanded_slices: Dict = field(default_factory=dict)
    label_colors: Dict = field(default_factory=dict)
    timed_refresh_immune_slices: List[str] = field(default_factory=list)
    cross_filters_enabled: bool = field(default=False)
    filter_scopes: Optional[Dict] = field(default_factory=dict)
    chart_configuration: Dict[str, ChartConfiguration] = ObjectField(cls=ChartConfiguration, dict_right=True, default_factory=dict)
    global_chart_configuration: GlobalChartconfiguration = ObjectField(cls=GlobalChartconfiguration, default_factory=GlobalChartconfiguration)
    default_filters: Dict = field(default_factory=dict)

    def add_chart(self, chart):
        chart_configuration = ChartConfiguration(id=chart.id)
        if self.global_chart_configuration.chartsInScope:
            for chart_id in self.global_chart_configuration.chartsInScope:
                if chart_id != chart.id:
                    chart_configuration.crossFilters.chartsInScope.append(chart_id)
        self.chart_configuration[str(chart.id)] = chart_configuration

        self.global_chart_configuration.chartsInScope.append(chart.id)

