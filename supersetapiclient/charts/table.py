"""Charts."""
from supersetapiclient.base.base import ObjectField
from supersetapiclient.charts.charts import Chart
from supersetapiclient.charts.options import Option
from supersetapiclient.charts.queries import AdhocMetric, Column, QueryObject, Metric, ColumnConfig, AdhocMetricColumn, \
    OrderBy
from supersetapiclient.charts.query_context import QueryContext
from dataclasses import dataclass, field
from typing import List, Dict
from supersetapiclient.charts.types import ChartType, DateFormatType, QueryModeType, TimeGrain, FilterExpressionType, \
    NumberFormatType, HorizontalAlignType, MetricType
from supersetapiclient.exceptions import ValidationError
from supersetapiclient.typing import Optional


@dataclass
class TableOption(Option):
    row_limit: int = 1000
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
    # columns: List[Column] = field(default_factory=list)
    column_config: Optional[Dict[str,ColumnConfig]] = ObjectField(cls=ColumnConfig, dict_right=True, default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        if not self.metrics:
            self.metrics: List[Metric] = []
        if self.server_page_length == 0:
            self.server_page_length = 10

    def validate(self, data: dict):
        super().validate(data)
        if not self.metrics:
            raise ValidationError(message='Field metrics cannot be empty.',
                                  solution='Use one of the add_simple_metric or add_custom_metric methods to add a queries.')

    def _add_column_config(self, label:str, column_config:ColumnConfig):
        self.column_config[label] = column_config

@dataclass
class TableFormData(TableOption):
    pass


@dataclass
class TableQueryObject(QueryObject):
    time_range: Optional[str] = field(init=False, default='No Filter')
    granularity: Optional[str] = None
    # applied_time_extras: List[str] = field(default_factory=list)

    def _add_simple_metric(self, metric:str, automatic_order: OrderBy):
        #In the table the option is sort descending
        automatic_order.sort_ascending = not automatic_order.sort_ascending
        super()._add_simple_metric(metric, automatic_order)

    def _add_custom_metric(self, label: str,
                           automatic_order: OrderBy,
                           column: AdhocMetricColumn = None,
                           sql_expression: str = None,
                           aggregate: MetricType = None):
        #In the table the option is sort descending
        automatic_order.sort_ascending = not automatic_order.sort_ascending
        super()._add_custom_metric(label, automatic_order, column, sql_expression, aggregate)


@dataclass
class TableQueryContext(QueryContext):
    form_data: TableFormData = ObjectField(cls=TableFormData, default_factory=TableFormData)
    queries: List[TableQueryObject] = ObjectField(cls=QueryObject, default_factory=list)

    def validate(self, data: dict):
        super().validate(data)
        if self.form_data.metrics or self.queries:
            equals = False
            counter = 0
            for form_data_metric in self.form_data.metrics:
                for query in self.queries:
                    for query_metric in query.metrics:
                        if form_data_metric == query_metric:
                            counter+=1
            if counter == len(self.form_data.metrics):
                equals = True

            if not equals:
                raise ValidationError(message='The metrics definition in formdata is not included in queries.metrics.',
                                      solution="We recommend using one of the Chart class's add_simple_metric or add_custom_metric methods to ensure data integrity.")

    def _guet_query_context_class(self):
        return TableQueryObject

@dataclass
class TableChart(Chart):
    viz_type: ChartType = ChartType.TABLE
    params: TableOption = ObjectField(cls=TableOption, default_factory=TableOption)
    query_context: TableQueryContext = ObjectField(cls=TableQueryContext, default_factory=TableQueryContext)

    def add_simple_metric(self, metric: MetricType,
                          automatic_order: OrderBy = OrderBy(),
                          column_config: ColumnConfig = None):
        super().add_simple_metric(metric, automatic_order)
        if column_config:
            self.params._add_column_config(str(metric), column_config)
            self.query_context.form_data._add_column_config(str(metric), column_config)


    def add_custom_metric(self, label: str,
                            automatic_order: OrderBy = OrderBy(),
                            column: AdhocMetricColumn = None,
                            sql_expression: str = None,
                            aggregate: MetricType = None,
                            column_config: ColumnConfig = None):
        super().add_custom_metric(label, automatic_order, column, sql_expression, aggregate)
        if column_config:
            self.params._add_column_config(label, column_config)
            self.query_context.form_data._add_column_config(label, column_config)
