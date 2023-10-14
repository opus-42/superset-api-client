"""Charts."""
from supersetapiclient.charts.charts import Chart
from supersetapiclient.charts.options import Option
from supersetapiclient.charts.queries import AdhocMetric, Column, QueryObject, Metric, ColumnConfig, AdhocMetricColumn, \
    MetricMixin
from supersetapiclient.charts.query_context import QueryContext
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from supersetapiclient.charts.types import ChartType, DateFormatType, QueryModeType, TimeGrain, FilterExpressionType, \
    NumberFormatType, HorizontalAlignType, MetricType


@dataclass
class TableOption(Option):
    viz_type: ChartType = ChartType.TABLE
    query_mode: QueryModeType = QueryModeType.AGGREGATE

    # order_by_cols: List = field(default_factory=list)

    server_pagination: Optional[bool] = False
    server_page_length: int = 0
    order_desc: bool = False
    show_totals: Optional[bool] = False

    table_timestamp_format: DateFormatType = DateFormatType.SMART_DATE
    page_length: Optional[int] = None
    include_search: Optional[bool] = False
    show_cell_bars: bool = True
    align_pn: Optional[bool] = False
    color_pn: bool = True
    allow_rearrange_columns: Optional[bool] = False

    column_config: Optional[Dict[str,ColumnConfig]] = field(default_factory=dict)

    conditional_formatting: Optional[List] = field(default_factory=list)

    ## percent_metrics: List = field(default_factory=list)
    ## all_columns: List = field(default_factory=list)

    metrics: Optional[List[Metric]] = field(default_factory=list)
    queryFields: Optional[Dict] = field(default_factory=dict)

    table_filter: Optional[bool] = False
    time_grain_sqla: Optional[TimeGrain] = None
    time_range: Optional[str] = 'No filter'

    columns: List[Column] = field(default_factory=list)
    granularity_sqla: Optional[str] = None

    def __post_init__(self):
        if self.server_page_length == 0:
            self.server_page_length = 10
        if self.row_limit == 0:
            self.row_limit = 1000

    def _add_simple_orderby(self, column_name:str, order:bool):
        self.order_by_cols.append([column_name, order])

    def _add_column_config(self, label:str, column_config:ColumnConfig):
        self.column_config[label] = column_config


@dataclass
class TableFormData(TableOption):
    pass


@dataclass
class TableQueryContext(QueryContext):
    form_data: TableFormData = field(default_factory=TableFormData)


@dataclass
class TableQueryObject(QueryObject):
    time_range: Optional[str] = field(init=False, default='No Filter')
    granularity: Optional[str] = None
    applied_time_extras: List[str] = field(default_factory=list)
    # columns: List[Column] = field(default_factory=list)

    def __post_init__(self):
        if not self.row_limit:
            self.row_limit = 1000


@dataclass
class TableChart(Chart):
    viz_type: ChartType = ChartType.TABLE
    params: TableOption = field(default_factory=TableOption)
    query_context: TableQueryContext = field(default_factory=TableQueryContext)

    def add_custom_metric(self, label: str,
                           sql_expression: str = None,
                           column: AdhocMetricColumn = None,
                           aggregate: MetricType = None,
                           column_config: ColumnConfig = None):
        super().add_custom_metric(label, sql_expression, column, aggregate)
        if column_config:
            self.params._add_column_config(label, column_config)

