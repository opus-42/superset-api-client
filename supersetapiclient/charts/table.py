"""Charts."""
from supersetapiclient.base.base import ObjectField
from supersetapiclient.charts.charts import Chart
from supersetapiclient.charts.options import Option
from supersetapiclient.charts.queries import AdhocMetric, Column, QueryObject, Metric, ColumnConfig, AdhocMetricColumn, \
    MetricMixin
from supersetapiclient.charts.query_context import QueryContext
from dataclasses import dataclass, field
from typing import List, Dict
from supersetapiclient.charts.types import ChartType, DateFormatType, QueryModeType, TimeGrain, FilterExpressionType, \
    NumberFormatType, HorizontalAlignType, MetricType
from supersetapiclient.typing import Optional


@dataclass
class TableOption(Option):
    viz_type: ChartType = ChartType.TABLE
    query_mode: QueryModeType = QueryModeType.AGGREGATE

    order_by_cols: List = field(default_factory=list)

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
    conditional_formatting: Optional[List] = field(default_factory=list)
    queryFields: Optional[Dict] = field(default_factory=dict)

    table_filter: Optional[bool] = False
    time_grain_sqla: Optional[TimeGrain] = None
    time_range: Optional[str] = 'No filter'
    granularity_sqla: Optional[str] = None

    metrics: Optional[List[Metric]] = ObjectField(cls=AdhocMetric, default_factory=list)
    columns: List[Column] = field(default_factory=list)
    column_config: Optional[Dict[str,ColumnConfig]] = ObjectField(cls=ColumnConfig, dict_right=True, default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        if not self.metrics:
            self.metrics: List[Metric] = []
        if not self.columns:
            self.columns: List[Column] = []
        if self.server_page_length == 0:
            self.server_page_length = 10
        if self.row_limit == 0:
            self.row_limit = 1000

    def _add_simple_orderby(self, column_name:str, order:bool):
        self.order_by_cols.append([column_name, order])

    def _add_column_config(self, label:str, column_config:ColumnConfig):
        self.column_config[label] = column_config

    def _add_custom_metric(self, label: str,
                            column: AdhocMetricColumn,
                            sql_expression: str = None,
                            aggregate: MetricType = None):
        super()._add_custom_metric(label, column, sql_expression, aggregate)
        self._new_query._add_custom_columns(label, column, sql_expression, aggregate)


@dataclass
class TableFormData(TableOption):
    pass


@dataclass
class TableQueryContext(QueryContext):
    form_data: TableFormData = ObjectField(cls=TableFormData, default_factory=TableFormData)


@dataclass
class TableQueryObject(QueryObject):
    time_range: Optional[str] = field(init=False, default='No Filter')
    granularity: Optional[str] = None
    applied_time_extras: List[str] = field(default_factory=list)
    # columns: List[Column] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.row_limit:
            self.row_limit = 1000


@dataclass
class TableChart(Chart):
    viz_type: ChartType = ChartType.TABLE
    params: TableOption = ObjectField(cls=TableOption, default_factory=TableOption)
    query_context: TableQueryContext = ObjectField(cls=TableQueryContext, default_factory=TableQueryContext)

    def add_custom_metric(self, label: str,
                          column: AdhocMetricColumn = None,
                           sql_expression: str = None,
                           aggregate: MetricType = None,
                           column_config: ColumnConfig = None):
        super().add_custom_metric(label, sql_expression, column, aggregate)
        if column_config:
            self.params._add_column_config(label, column_config)


