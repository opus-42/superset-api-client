import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from supersetapiclient.base.base import Object, default_string
from supersetapiclient.charts.filters import AdhocFilterClause
from supersetapiclient.charts.types import ChartType, LabelType, LegendOrientationType, LegendType, DateFormatType, \
    NumberFormatType, CurrentPositionType, CurrencyCodeType
from supersetapiclient.exceptions import ChartValidationError


@dataclass
class CurrencyFormat(Object):
    symbolPosition: CurrentPositionType = None
    symbol: CurrencyCodeType = None


@dataclass
class Option(Object):
    viz_type: ChartType = None
    slice_id: Optional[int] = None

    datasource: str = None

    color_scheme: str = default_string(default='supersetColors')
    legendType: LegendType = LegendType.SCROLL
    legendOrientation: LegendOrientationType = LegendOrientationType.TOP
    show_legend: bool = True
    show_labels: bool = True
    legendMargin: int = None
    currency_format: CurrencyFormat = field(default_factory=CurrencyFormat)
    number_format: NumberFormatType = NumberFormatType.SMART_NUMBER
    date_format: DateFormatType = DateFormatType.SMART_DATE

    adhoc_filters: List[AdhocFilterClause] = field(default_factory=list)
    # dashboards: List[int] = field(default_factory=list)
    groupby: List[str] = field(default_factory=list)


@dataclass
class PieOption(Option):
    viz_type: ChartType = ChartType.PIE
    label_type: LabelType = LabelType.CATEGORY_NAME
    metric: str = 'count'
    donut: bool = False
    label_line: bool = False
    labels_outside: bool = True
    show_total: bool = False
    sort_by_metric: bool = True
    innerRadius: int = 30
    outerRadius: int = 70
    show_labels_threshold: int = 3
    row_limit: int = 100

    def __post_init__(self):
        if self.donut and self.innerRadius != 30:
            self.donut = True
        if self.legendMargin:
            self.show_legend = True
        if self.label_line:
            self.labels_outside = True
            self.show_labels = True
        if self.labels_outside:
            self.show_labels = True


# 'metric': {'aggregate': 'SUM',
#            'column': {'column_name': 'sales',
#                       'description': None,
#                       'expression': None,
#                       'filterable': True,
#                       'groupby': True,
#                       'id': 917,
#                       'is_dttm': False,
#                       'optionName': '_col_Sales',
#                       'python_date_format': None,
#                       'type': 'DOUBLE '
#                               'PRECISION',
#                       'verbose_name': None},
#            'expressionType': 'SIMPLE',
#            'hasCustomLabel': False,
#            'isNew': False,
#            'label': '(Sales)',
#            'optionName': 'metric_3sk6pfj3m7i_64h77bs4sly',
#            'sqlExpression': None},