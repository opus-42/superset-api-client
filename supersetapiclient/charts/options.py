from dataclasses import dataclass, field
from typing import List, Dict, Optional
from supersetapiclient.base.base import Object, ObjectField
from supersetapiclient.charts.filters import AdhocFilterClause
from supersetapiclient.charts.queries import OrderBy, MetricMixin, AdhocMetric, AdhocMetricColumn
from supersetapiclient.charts.types import ChartType, FilterOperatorType, FilterClausesType, \
    FilterExpressionType, MetricType


@dataclass
class Option(Object, MetricMixin):
    viz_type: ChartType = None
    slice_id: [int] = None

    datasource: str = None

    extra_form_data: Dict = field(default_factory=dict)
    row_limit: int = 100

    adhoc_filters: List[AdhocFilterClause] =  ObjectField(cls=AdhocFilterClause, default_factory=list)
    dashboards: List[int] = field(default_factory=list)
    groupby: Optional[List[OrderBy]] = ObjectField(cls=AdhocMetric, default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.groupby:
            self.groupby: List[OrderBy] = []

    def add_dashboard(self, dashboard_id):
        dashboards = set(self.dashboards)
        dashboards.add(dashboard_id)
        self.dashboards = list(dashboards)

    def _add_simple_filter(self, column_name: str,
                           value: str,
                           operator: FilterOperatorType = FilterOperatorType.EQUAL,
                           clause: FilterClausesType = FilterClausesType.WHERE) -> None:
        adhoc_filter_clause = AdhocFilterClause(comparator=value,
                                                subject=column_name,
                                                clause=clause,
                                                operator=operator,
                                                expressionType=FilterExpressionType.SIMPLE)

        self.adhoc_filters.append(adhoc_filter_clause)

