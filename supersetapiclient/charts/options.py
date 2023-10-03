import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, asdict
from typing import List, Optional

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.base.currency_format import CurrencyCode, CurrentPosition
from supersetapiclient.charts.filters import AdhocFilterClause
from supersetapiclient.charts.types import ChartType, LabelType, LegendOrientationType, LegendType

D3_TIME_FORMAT_OPTIONS = [
  ['smart_date', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%H:%M:%S']
]
# D3_FORMAT_DOCS,
# D3_NUMBER_FORMAT_DESCRIPTION_VALUES_TEXT,
# D3_FORMAT_OPTIONS,
# D3_TIME_FORMAT_OPTIONS,
@dataclass
class CurrencyFormat(Object):
    symbolPosition: CurrentPosition = None
    symbol: CurrencyCode = None


@dataclass
class Option(Object):
    viz_type: ChartType = None
    slice_id: Optional[int] = None

    number_format: str = default_string(default='SMART_NUMBER')
    datasource: str = default_string()

    color_scheme: str = default_string(default='supersetColors')
    legendMargin: int = field(default=0)
    show_total: bool = field(default=False)
    show_labels: bool = field(default=False)
    show_legend: bool = field(default=True)
    metric: str = default_string(default='count')
    row_limit: int = field(default=100)
    sort_by_metric: bool = field(default=False)
    currency_format: CurrencyFormat = field(default_factory=CurrencyFormat)
    number_format: str = default_string(default='SMART_NUMBER')
    date_format: str = default_string(default='smart_date')

    adhoc_filters: List[AdhocFilterClause] = field(default_factory=list)

    dashboards: List[int] = field(default_factory=list)
    groupby: List[str] = field(default_factory=list)

    # @abstractmethod
    def to_dict(self, columns=None):
        data = super().to_dict(columns)
        data['currency_format'] = self.currency_format.to_dict()
        adhoc_filters = []
        for _adhoc_filter in data['adhoc_filters']:
            adhoc_filters.append(_adhoc_filter.to_dict())
        data['adhoc_filters'] = adhoc_filters
        return data

    # @abstractmethod
    def to_json(self, columns=None):
        data = super().to_json(columns)
        return json.dumps(data)

    @classmethod
    def from_json(cls, data: dict):
        obj = super().from_json(data)
        obj.currency_format = CurrencyFormat.from_json(data['currency_format'])
        obj.adhoc_filters = []
        for field in data['adhoc_filters']:
            obj.adhoc_filters.append(AdhocFilterClause.from_json(field))
        return obj


@dataclass
class PieOption(Option):
    viz_type: ChartType = ChartType.PIE
    donut: bool = field(default=False)
    innerRadius: int = field(default=30)
    label_line: bool = field(default=False)
    label_type: LabelType = LabelType.CATEGORI_VALUE_AND_PERCENTAG
    legendOrientation: LegendOrientationType = LegendOrientationType.BOTTOM
    legendType: LegendType = LegendType.PLAIN

    labels_outside: bool = field(default=False)
    outerRadius: int = field(default=70)
    show_labels_threshold: int = field(default=5)

