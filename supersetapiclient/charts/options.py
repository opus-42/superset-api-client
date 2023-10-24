from dataclasses import dataclass, field
from typing import List, Dict, Optional
from supersetapiclient.base.base import Object, ObjectField
from supersetapiclient.charts.filters import AdhocFilterClause
from supersetapiclient.charts.queries import OrderByTyping, QueryMetricMixin, AdhocMetric, AdhocMetricColumn, OrderBy
from supersetapiclient.charts.types import ChartType, FilterOperatorType, FilterClausesType, \
    FilterExpressionType, MetricType
from supersetapiclient.exceptions import ValidationError


class OptionMetricMixin(QueryMetricMixin):
    def _add_simple_groupby(self, column_name:str):
        self.groupby.append(column_name)

    def _add_custom_groupby(self, label: str,
                            column: AdhocMetricColumn = None,
                            sql_expression: str = None,
                            aggregate: MetricType = None):
        metric = self._get_metric(label, column, sql_expression, aggregate)
        if column:
            metric.expressionType = FilterExpressionType.CUSTOM_SQL
            column.expressionType = FilterExpressionType.CUSTOM_SQL
        self.groupby.append(metric)

    def _add_simple_metric(self, metric:str, automatic_order: OrderBy):
        super()._add_simple_metric(metric, automatic_order)

    def _add_custom_metric(self, label: str,
                           automatic_order: OrderBy,
                           column: AdhocMetricColumn = None,
                           sql_expression: str = None,
                           aggregate: MetricType = None):
        metric = self._get_metric(label, column, sql_expression, aggregate)
        self.metrics.append(metric)


@dataclass
class Option(Object, OptionMetricMixin):
    viz_type: ChartType = None
    slice_id: [int] = None

    datasource: str = None

    extra_form_data: Dict = field(default_factory=dict)
    row_limit: int = 100

    adhoc_filters: List[AdhocFilterClause] =  ObjectField(cls=AdhocFilterClause, default_factory=list)
    dashboards: List[int] = field(default_factory=list)
    groupby: Optional[List[OrderByTyping]] = ObjectField(cls=AdhocMetric, default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.groupby:
            self.groupby: List[OrderByTyping] = []

    def validate(self, data: dict):
        super().validate(data)
        if not self.groupby:
            raise ValidationError(message='Field groupy cannot be empty.',
                                  solution='Use one of the add_simple_groupby or add_custom_groupby methods to add a groupby.')

    def add_dashboard(self, dashboard_id):
        dashboards = set(self.dashboards)
        dashboards.add(dashboard_id)
        self.dashboards = list(dashboards)

    def _add_simple_filter(self, column_name: str,
                           value: str,
                           operator: FilterOperatorType = FilterOperatorType.EQUALS,
                           clause: FilterClausesType = FilterClausesType.WHERE) -> None:
        adhoc_filter_clause = AdhocFilterClause(comparator=value,
                                                subject=column_name,
                                                clause=clause,
                                                operator=operator,
                                                operatorId=operator.name,
                                                expressionType=FilterExpressionType.SIMPLE)
        self.adhoc_filters.append(adhoc_filter_clause)

