"""Charts."""
from supersetapiclient.charts.charts import Chart
from supersetapiclient.charts.options import Option
from supersetapiclient.charts.queries import Metric, CurrencyFormat, MetricMixin, AdhocMetricColumn, AdhocMetric
from supersetapiclient.charts.query_context import QueryContext
from dataclasses import dataclass, field
from supersetapiclient.base.base import default_string, ObjectField
from supersetapiclient.charts.types import ChartType, LabelType, LegendOrientationType, LegendType, DateFormatType, \
    NumberFormatType, MetricType
from supersetapiclient.exceptions import ValidationError
from supersetapiclient.typing import Optional


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

    def _add_simple_metric(self, metric:str, order:bool):
        self._check_metric(metric)
        self.metric = metric
        self.sort_by_metric = order

    def _add_custom_metric(self, label: str,
                           sql_expression: str = None,
                           column: AdhocMetricColumn = None,
                           aggregate: MetricType = None):
        metric = self._get_metric(label, sql_expression, column, aggregate)
        self.metric = metric



@dataclass
class PieFormData(PieOption):
    pass


@dataclass
class PieQueryContext(QueryContext):
    form_data: PieFormData = ObjectField(cls=PieFormData, default_factory=PieFormData)
    # self.queries[0]
    # self.queries[0].metrics
    def validate(self, data: dict):
        if self.form_data.metric or self.queries:
            equals = False
            for query in self.queries:
                for metric in query.metrics:
                    if self.form_data.metric == metric:
                        equals = True
            if not equals:
                raise ValidationError(message='The metric definition in formdata is not included in queries.metrics.',
                                      solution="We recommend using one of the Chart class's add_simple_metric or add_custom_metric methods to ensure data integrity.")

        equals = False
        if self.form_data.groupby or self.queries:
            for query in self.queries:
                if self.form_data.groupby == query.columns:
                    equals = True
        if not equals:
            raise ValidationError(message='The dimensions defined in self.form_data differ from self.queries.',
                                  solution="We recommend using one of the Chart class's add_simple_groupby or add_custom_groupby methods to ensure data integrity.")

@dataclass
class PieChart(Chart):
    viz_type: ChartType = ChartType.PIE
    params: PieOption =  ObjectField(cls=PieOption, default_factory=PieOption)
    query_context: PieQueryContext =  ObjectField(cls=PieQueryContext, default_factory=PieQueryContext)
