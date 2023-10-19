import logging
from dataclasses import dataclass
from typing import List, Union, Literal, get_args

from supersetapiclient.base.base import Object, ObjectField, default_string
from supersetapiclient.charts.types import FilterOperatorType, TimeGrain, FilterExpressionType, SqlMapType, \
    GenericDataType, HorizontalAlignType, NumberFormatType, CurrentPositionType, CurrencyCodeType, MetricType
from supersetapiclient.exceptions import ValidationError
from supersetapiclient.typing import FilterValues, Optional

logger = logging.getLogger(__name__)

@dataclass
class CurrencyFormat(Object):
    symbolPosition: CurrentPositionType = None
    symbol: CurrencyCodeType = None


@dataclass
class ColumnConfig(Object):
    horizontalAlign: HorizontalAlignType = HorizontalAlignType.LEFT
    d3NumberFormat: Optional[NumberFormatType] = NumberFormatType.ORIGINAL_VALUE
    alignPositiveNegative: Optional[bool] = None
    colorPositiveNegative: Optional[bool] = None
    showCellBars: Optional[bool] = None
    columnWidth: Optional[int] = None
    currency_format: Optional[CurrencyFormat] = ObjectField(cls=CurrencyFormat, default_factory=CurrencyFormat)


@dataclass
class QuerieExtra(Object):
    time_grain_sqla: Optional[TimeGrain] = None
    having: str = ''
    where: str = ''


@dataclass
class AdhocColumn(Object):
    hasCustomLabel: Optional[bool]
    label: str
    sqlExpression: str
    columnType: Optional[Literal["BASE_AXIS", "SERIES"]]
    timeGrain: Optional[str]
Column = Union[AdhocColumn, str]


@dataclass
class QueryFilterClause(Object):
    col: Column
    val: Optional[FilterValues]
    op: FilterOperatorType = FilterOperatorType.EQUAL


@dataclass
class AdhocMetricColumn(Object):
    column_name: str = default_string()
    id: Optional[int] = None
    verbose_name: Optional[str] = None
    description: Optional[str] = None
    expression: Optional[str] = None
    filterable: bool = True
    groupby: bool = True
    is_dttm: bool = False
    python_date_format: Optional[str] = None
    type: SqlMapType = None
    type_generic: Optional[GenericDataType] = None


    def validate(self, data: dict):
        if not self.column_name or self.type:
            raise ValidationError(message='At least the column_name and type fields must be informed.',
                                  solution='')

@dataclass
class AdhocMetric(Object):
    label: Optional[str] = default_string()
    expressionType: FilterExpressionType = FilterExpressionType.CUSTOM_CQL
    sqlExpression: Optional[str] = None
    hasCustomLabel: Optional[bool] = False
    column: Optional[AdhocMetricColumn] = ObjectField(cls=AdhocMetricColumn, default_factory=AdhocMetricColumn)
    aggregate: Optional[MetricType] = None


Metric = Union[AdhocMetric, Literal['count', 'sum', 'avg', 'min', 'max', 'count distinct']]
OrderBy = tuple[Metric, bool]

class MetricMixin:
    def _get_metric(self, label: str,
                        column: AdhocMetricColumn = None,
                        sql_expression: str = None,
                        aggregate: MetricType = MetricType.COUNT):
        expression_type = FilterExpressionType.SIMPLE
        if sql_expression:
            expression_type = FilterExpressionType.CUSTOM_CQL

        if aggregate:
            self._check_metric(aggregate)
            aggregate = str(aggregate).upper()

        _metric = {
            "expressionType": str(expression_type),
            "hasCustomLabel": True,
        }
        if label:
            _metric['label'] = label
        if sql_expression:
            _metric['sqlExpression'] = sql_expression
        if column:
            _metric['column'] = column
        if aggregate:
            _metric['aggregate'] = aggregate

        return AdhocMetric(**_metric)

    def _check_metric(self, value):
        simple_metrics = get_args(get_args(Metric)[-1])
        if str(value) not in simple_metrics:
            raise ValidationError(message='Metric not found.',
                                  solution=f'Use one of the options:{simple_metrics}')

    def _add_simple_metric(self, metric:str):
        self._check_metric(metric)
        if not self.metrics or (get_args(self.metrics) and get_args(self.metrics)[0] == Metric):
            self.metrics: List[str] = []
        self.metrics.append(metric)

    def _add_custom_metric(self, label: str,
                           column: AdhocMetricColumn = None,
                           sql_expression: str = None,
                           aggregate: MetricType = None):
        metric = self._get_metric(label, column, sql_expression, aggregate)
        if isinstance(self.metrics, list):
            self.metrics.append(metric)

    def _add_custom_columns(self, label: str,
                           column: AdhocMetricColumn = None,
                           sql_expression: str = None,
                           aggregate: MetricType = None):
        metric = self._get_metric(label, column, sql_expression, aggregate)
        if isinstance(self.columns, list):
            self.columns.append(metric)
        if column:
            column.expressionType = FilterExpressionType.CUSTOM_CQL

    def _add_custom_orderby(self, label: str,
                           column: AdhocMetricColumn,
                           sql_expression: str = None,
                           aggregate: MetricType = None):
        metric = self._get_metric(label, column, sql_expression, aggregate)
        if isinstance(self.orderby, list):
            self.orderby.append((metric, False))

    def _add_simple_groupby(self, column_name:str, self_field: str = 'groupby'):
        dimensions = getattr(self, self_field)
        if not dimensions:
            dimensions = []
        dimensions.append(column_name)
        setattr(self, self_field, dimensions)

    def _add_custom_groupby(self, label: str,
                            column: AdhocMetricColumn = None,
                            sql_expression: str = None,
                            aggregate: MetricType = None):
        metric = self._get_metric(label, column, sql_expression, aggregate)
        if isinstance(self.groupby, list):
            self.groupby.append(metric)
        if column:
            column.expressionType = FilterExpressionType.CUSTOM_CQL


@dataclass
class QueryObject(Object, MetricMixin):
    row_limit: Optional[int] = 0
    series_limit: Optional[int] = None
    series_limit_metric: Optional[Metric] = ObjectField(cls=AdhocMetric, default_factory=AdhocMetric)
    order_desc: bool = True
    orderby: Optional[List[OrderBy]] = ObjectField(cls=AdhocMetric, default_factory=list)

    filters: List[QueryFilterClause] = ObjectField(cls=QueryFilterClause, default_factory=list)
    extras: QuerieExtra = ObjectField(cls=QuerieExtra, default_factory=QuerieExtra)
    columns: Optional[List[Metric]] =  ObjectField(cls=AdhocMetric, default_factory=list)
    metrics: Optional[List[Metric]] =  ObjectField(cls=AdhocMetric, default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.metrics:
            self.metrics:List[Metric] = []
        if not self.orderby:
            self.orderby:List[OrderBy] = []
        if not self.columns:
            self.columns:List[Metric] = []
        if not self.row_limit == 0:
            self.row_limit = 100

    def validate(self, data: dict):
        pass

    def _add_simple_filter(self, column_name: Column,
                           value: FilterValues,
                           operator: FilterOperatorType = FilterOperatorType.EQUAL) -> None:
        query_filter_clause = QueryFilterClause(col=column_name, val=value, op=operator)
        self.filters.append(query_filter_clause)

    def _add_simple_groupby(self, column_name: str):
        super()._add_simple_groupby(column_name, 'columns')


@dataclass
class PieQuerie(Object):
    pass


