from dataclasses import dataclass, field
from typing import List, Optional, Union, Literal, get_args

from supersetapiclient.base.base import Object
from supersetapiclient.charts.types import FilterOperatorType, TimeGrain, FilterExpressionType, SqlMapType, \
    GenericDataType, HorizontalAlignType, NumberFormatType, CurrentPositionType, CurrencyCodeType, MetricType
from supersetapiclient.exceptions import ValidationError
from supersetapiclient.typing import FilterValues

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
    currency_format: Optional[CurrencyFormat] = field(default_factory=CurrencyFormat)


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
    column_name: str
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
    label: Optional[str]
    expressionType: FilterExpressionType = FilterExpressionType.CUSTOM_CQL
    sqlExpression: Optional[str] = None
    column: Optional[AdhocMetricColumn] = field(default_factory=Column)
    aggregate: MetricType = None
    hasCustomLabel: Optional[bool] = False

Metric = Union[AdhocMetric, Literal['count', 'sum', 'avg', 'min', 'max', 'count distinct']]
OrderBy = tuple[Metric, bool]


class MetricMixin:
    def _get_metric(self, label: str,
                           sql_expression: str = None,
                           column: AdhocMetricColumn = None,
                           aggregate: MetricType = None):
        expression_type = FilterExpressionType.CUSTOM_CQL
        if column:
            expression_type = FilterExpressionType.SIMPLE

        if aggregate:
            self._check_metric(aggregate)
            aggregate = str(aggregate).upper()

        _metric = {
            "label": label,
            "expressionType": str(expression_type),
            "sqlExpression": sql_expression,
            "column": column,
            "aggregate": aggregate,
            "hasCustomLabel": True,
        }
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
                           sql_expression: str = None,
                           column: AdhocMetricColumn = None,
                           aggregate: MetricType = None,
                           self_field: str = 'metrics'):
        metric = self._get_metric(label, sql_expression, column, aggregate)
        if not self.metrics or (get_args(self.metrics) and get_args(self.metrics)[0] == Metric):
            self.metrics: List[Metric] = []
        self.metrics.append(metric)

    def _add_simple_groupby(self, column_name:str, self_field: str = 'groupby'):
        dimensions = getattr(self, self_field)
        if not dimensions or (get_args(dimensions) and get_args(dimensions)[0] == OrderBy):
            dimensions: List[str] = []
        dimensions.append(column_name)
        setattr(self, self_field, dimensions)

    def _add_custom_groupby(self, label: str,
                            sql_expression: str = None,
                            column: AdhocMetricColumn = None,
                            aggregate: MetricType = None,
                            self_field: str = 'groupby'):

        metric = self._get_metric(label, sql_expression, column, aggregate)

        dimensions = getattr(self, self_field)
        if not dimensions or (get_args(dimensions) and get_args(dimensions)[0] == OrderBy):
            dimensions: List[str] = []
        dimensions.append(metric)
        setattr(self, self_field, dimensions)


@dataclass
class QueryObject(Object, MetricMixin):
    filters: List[QueryFilterClause] = field(default_factory=list)
    extras: QuerieExtra = field(default_factory=QuerieExtra)
    columns: Optional[list[Metric]] = None
    metrics: Optional[list[Metric]] = None
    #
    row_limit: Optional[int] = 0
    series_limit: Optional[int] = None
    series_limit_metric: Optional[Metric] = None
    order_desc: bool = True
    orderby: Optional[list[OrderBy]] = None

    def __post_init__(self):
        # if not self.metrics:
        #     self.metrics = ['count']
        # if not self.orderby:
        #     self.orderby = [["count", False]]
        if not self.row_limit == 0:
            self.row_limit = 100

    def validate(self, data: dict):
        pass

    def _add_simple_filter(self, column_name: Column, value: FilterValues, operator: FilterOperatorType = FilterOperatorType.EQUAL) -> None:
        query_filter_clause = QueryFilterClause(col=column_name, val=value, op=operator)
        self.filters.append(query_filter_clause)

    def _add_simple_groupby(self, column_name: str):
        super()._add_simple_groupby(column_name, 'columns')

    def _add_custom_groupby(self, label: str,
                            sql_expression: str = None,
                            column: AdhocMetricColumn = None,
                            aggregate: MetricType = None):
        super()._add_custom_groupby(label, sql_expression, column, aggregate, 'columns')

    # "columns": [
    #     {
    #         "expressionType": "SQL",
    #         "label": "Pergunta",
    #         "sqlExpression": "split_part(resposta_nome,'::',-1)"
    #     }
    # ],


    # def _add_simple_orderby(self, column_name:str, order:bool):
    #     self.orderby.append([column_name, order])
    # #     "metrics": ["count"], "orderby": [["count", false]]
    #
    #
    # def _add_custom_orderby(self, label: str,
    #                        sql_expression: str = None,
    #                        column: AdhocMetricColumn = None,
    #                        aggregate: MetricType = None):
    #     metric = self._get_metric(label, sql_expression, column, aggregate)
    #
    #     # self.metrics
    #
    #     if not self.groupby:
    #         self.groupby = List[OrderBy]
    #     self.orderby.append(metric)



@dataclass
class PieQuerie(Object):
    pass

