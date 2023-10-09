import json
from dataclasses import dataclass, field
from typing import List

from supersetapiclient.base.base import Object
from supersetapiclient.base.datasource import DataSource
from supersetapiclient.charts.options import Option
from supersetapiclient.charts.queries import QueryObject, AdhocMetricColumn
from supersetapiclient.charts.types import FilterOperatorType, FilterClausesType, MetricType
from supersetapiclient.exceptions import ChartValidationError


@dataclass
class FormData(Option):
    pass


@dataclass
class QueryContext(Object):
    datasource: DataSource = field(default_factory=DataSource)
    queries: List[QueryObject] = field(default_factory=list)
    form_data: FormData = field(default_factory=FormData)

    def add_dashboard(self, dashboard_id):
        self.form_data.add_dashboard(dashboard_id)

    @property
    def _new_query(self):
        if self.queries and len(self.queries) > 1:
            raise ChartValidationError("""There are more than one query in the queries list. 
                                       We don't know which one to include the filter in.""")
        if not self.queries:
            self.queries = []
        if len(self.queries) == 0:
            self.queries.append(QueryObject())
        return self.queries[-1]

    def _add_simple_metric(self, metric: str, order: bool):
        self.form_data._add_simple_metric(metric, order)
        self._new_query._add_simple_metric(metric)

    def _add_custom_metric(self, label: str,
                           sql_expression: str = None,
                           column: AdhocMetricColumn = None,
                           aggregate: MetricType = None):
        self.form_data._add_custom_metric(label, sql_expression, column, aggregate)
        self._new_query._add_custom_metric(label, sql_expression, column, aggregate)

    def _add_simple_groupby(self, column_name: str):
        self.form_data._add_simple_groupby(column_name)
        self._new_query._add_simple_groupby(column_name)

    def _add_custom_groupby(self, label: str,
                            sql_expression: str = None,
                            column: AdhocMetricColumn = None,
                            aggregate: MetricType = None):
        self.form_data._add_custom_groupby(label, sql_expression, column, aggregate)
        self._new_query._add_custom_groupby(label, sql_expression, column, aggregate)


    def _add_simple_filter(self, column_name: str,
                          value: str,
                          operator: FilterOperatorType = FilterOperatorType.EQUAL,
                          clause: FilterClausesType = FilterClausesType.WHERE) -> None:
        self.form_data._add_simple_filter(column_name, value, operator, clause)
        self._new_query._add_simple_filter(column_name, value, operator)