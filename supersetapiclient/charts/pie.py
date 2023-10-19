"""Charts."""
from typing import List

from supersetapiclient.charts.charts import Chart
from supersetapiclient.charts.options import Option
from supersetapiclient.charts.queries import Metric, CurrencyFormat, MetricMixin, AdhocMetricColumn, AdhocMetric, \
    OrderBy, QueryObject
from supersetapiclient.charts.query_context import QueryContext
from dataclasses import dataclass, field
from supersetapiclient.base.base import default_string, ObjectField
from supersetapiclient.charts.types import ChartType, LabelType, LegendOrientationType, LegendType, DateFormatType, \
    NumberFormatType, MetricType
from supersetapiclient.exceptions import ValidationError
from supersetapiclient.typing import Optional
from supersetapiclient.utils import dict_compare


@dataclass
class PieOption(Option):
    viz_type: ChartType = ChartType.PIE
    color_scheme: str = default_string(default='supersetColors')
    legendType: LegendType = LegendType.SCROLL
    legendOrientation: LegendOrientationType = LegendOrientationType.TOP
    label_type: LabelType = LabelType.CATEGORY_NAME
    show_legend: bool = True
    show_labels: bool = True
    legendMargin: Optional[int] = None
    currency_format: Optional[CurrencyFormat] = ObjectField(cls=CurrencyFormat, default_factory=CurrencyFormat)
    number_format: NumberFormatType = NumberFormatType.SMART_NUMBER
    date_format: DateFormatType = DateFormatType.SMART_DATE
    donut: Optional[bool] = False
    label_line: Optional[bool] = False
    labels_outside: bool = True
    show_total: Optional[bool] = False
    innerRadius: int = 30
    outerRadius: int = 70
    show_labels_threshold: int = 5
    metric: Metric = ObjectField(AdhocMetric, default=None)
    sort_by_metric: bool = True

    def __post_init__(self):
        super().__post_init__()
        if self.donut and self.innerRadius != 30:
            self.donut = True
        if self.legendMargin:
            self.show_legend = True
        if self.label_line:
            self.labels_outside = True
            self.show_labels = True
        if self.labels_outside:
            self.show_labels = True

    def validate(self, data: dict):
        super().validate(data)
        if not self.groupby:
            raise ValidationError(message='Field groupy cannot be empty.',
                                  solution='Use one of the add_simple_groupby or add_custom_groupby methods to add a groupby.')

        if not self.metric:
            raise ValidationError(message='Field metric cannot be empty.',
                                  solution='Use one of the add_simple_metric or add_custom_metric methods to add a metric.')

        if not self.metric.column.column_name \
                or not self.metric.column.type:
            raise ValidationError(message='Fields self.metric.column.column_name and self.metric.column.type cannot be empty.',
                                  solution='Use one of the add_simple_metric or add_custom_metric methods to add a metric.')

    def _add_simple_metric(self, metric:MetricType.COUNT, order:bool=True):
        self._check_metric(metric)
        self.metric = str(metric)
        self.sort_by_metric = order

    def _add_custom_metric(self, label: str,
                            column: AdhocMetricColumn,
                            sql_expression: str = None,
                            aggregate: MetricType = None):
        if aggregate is None:
            raise ValidationError(message='Argument aggregate cannot be empty.')
        self.metric = self._get_metric(label, column, sql_expression, aggregate)

@dataclass
class PieFormData(PieOption):
    pass


@dataclass
class QueryObjectPie(QueryObject):
    def validate(self, data: dict):
        super().validate(data)
        if not self.metric:
            raise ValidationError(message='Field orderby cannot be empty.',
                                  solution='Use one of the add_simple_metric or add_custom_metric methods to add a orderby.')
        if not self.orderby:
            raise ValidationError(message='Field orderby cannot be empty.',
                                  solution='Use one of the add_simple_metric or add_custom_metric methods to add a orderby.')

    def _add_simple_metric(self, metric: str, order: bool):
        self._check_metric(metric)
        self.form_data._add_simple_metric(metric, order)
        self.orderby.append((metric, order))

    def _add_custom_metric(self, label: str,
                           column: AdhocMetricColumn,
                           sql_expression: str = None,
                           aggregate: MetricType = None):

        super()._add_custom_metric(label, column, sql_expression, aggregate)
        self._add_custom_orderby(label, column, sql_expression, aggregate)


@dataclass
class PieQueryContext(QueryContext):
    form_data: PieFormData = ObjectField(cls=PieFormData, default_factory=PieFormData)
    queries: List[QueryObjectPie] = ObjectField(cls=QueryObjectPie, default_factory=list)

    def __post_init__(self):
        super().__post_init__()

    def _guet_query_context_class(self):
        return QueryObjectPie

    def validate(self, data: dict):
        if not self.queries:
            raise ValidationError(message='Field queries cannot be empty.',
                                  solution='Use one of the add_simple_metric or add_custom_metric methods to add a queries.')
        equals = False
        if self.form_data.metric or self.queries:
            for query in self.queries:
                for metric in query.metrics:
                    if self.form_data.metric == metric:
                        equals = True
                        break
            if not equals:
                raise ValidationError(message='The metric definition in formdata is not included in queries.metrics.',
                                      solution="We recommend using one of the Chart class's add_simple_metric or add_custom_metric methods to ensure data integrity.")

        equals = False
        if self.form_data.metric or self.queries:
            equals = False
            for query in self.queries:
                for order in query.orderby:
                    if not isinstance(order, tuple):
                        raise ValidationError('Order by must be a tuple.',
                                              slution="We recommend using one of the Chart class's add_simple_metric or add_custom_metric methods to ensure data integrity.")
                    if self.form_data.metric == order[0]:
                        equals = True
                        break
            if not equals:
                raise ValidationError(message='The metric definition in formdata is not included in queries.orderby.',
                                      solution="We recommend using one of the Chart class's add_simple_metric or add_custom_metric methods to ensure data integrity.")


@dataclass
class PieChart(Chart):
    viz_type: ChartType = ChartType.PIE
    params: PieOption =  ObjectField(cls=PieOption, default_factory=PieOption)
    query_context: PieQueryContext =  ObjectField(cls=PieQueryContext, default_factory=PieQueryContext)

    def validate(self, data: dict):
        super().validate(data)
        if (self.params.metric or self.query_context.form_data.metric) and not (self.params.metric == self.query_context.form_data.metric):
                raise ValidationError(message='The metric definition in self.params.metric not equals self.query_context.form_data.metric.',
                                      solution="We recommend using one of the Chart class's add_simple_metric or add_custom_metric methods to ensure data integrity.")

    # def add_custom_metric(self, label: str,
    #                         column: AdhocMetricColumn,
    #                         sql_expression: str = None,
    #                         aggregate: MetricType = None):
    #     super().add_custom_metric(label, column, sql_expression, aggregate )
