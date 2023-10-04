import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, asdict, MISSING
from typing import List, Optional

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.charts.filters import AdhocFilterClause
from supersetapiclient.charts.types import ChartType, LabelType, LegendOrientationType, LegendType, DateFormatType, \
    NumberFormatType, CurrentPositionType, CurrencyCodeType

D3_TIME_FORMAT_OPTIONS = [
  ['smart_date', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%H:%M:%S']
]
# D3_FORMAT_DOCS,
# D3_NUMBER_FORMAT_DESCRIPTION_VALUES_TEXT,
# D3_FORMAT_OPTIONS,
# D3_TIME_FORMAT_OPTIONS,
@dataclass
class CurrencyFormat(Object):
    symbolPosition: CurrentPositionType = None
    symbol: CurrencyCodeType = None

    # @classmethod
    # def from_json(cls, data: dict):
    #     return super().from_json(data)


@dataclass
class Option(Object):
    viz_type: ChartType = None
    slice_id: Optional[int] = None

    datasource: str = field(default=None)

    color_scheme: str = default_string(default='supersetColors')
    legendMargin: int = field(default=0)
    show_total: bool = field(default=False)
    show_labels: bool = field(default=True)
    show_legend: bool = field(default=True)
    metric: str = default_string(default='count')
    row_limit: int = field(default=100)
    sort_by_metric: bool = field(default=True)
    currency_format: CurrencyFormat = field(default_factory=CurrencyFormat)
    number_format: NumberFormatType = NumberFormatType.ORIGINAL_VALUE
    date_format: DateFormatType = DateFormatType.SMART_DATE

    adhoc_filters: List[AdhocFilterClause] = field(default_factory=list)

    dashboards: List[int] = field(default_factory=list)
    groupby: List[str] = field(default_factory=list)


@dataclass
class PieOption(Option):
    viz_type: ChartType = ChartType.PIE
    donut: bool = field(default=False)
    innerRadius: int = field(default=30)
    label_line: bool = field(default=True)
    label_type: LabelType = LabelType.CATEGORI_VALUE_AND_PERCENTAG
    legendOrientation: LegendOrientationType = LegendOrientationType.BOTTOM
    legendType: LegendType = LegendType.PLAIN

    labels_outside: bool = field(default=True)
    outerRadius: int = field(default=70)
    show_labels_threshold: int = field(default=5)
