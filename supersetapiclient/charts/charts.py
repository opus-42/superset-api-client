"""Charts."""
import copy
import json
from dataclasses import dataclass, field
from typing import Optional
from typing_extensions import Self

from supersetapiclient.base.base import Object, ObjectFactories, default_string, raise_for_status, json_field
from supersetapiclient.charts.filters import AdhocFilterClause
from supersetapiclient.charts.options import Option, PieOption
from supersetapiclient.charts.queries import QueryFilterClause

from supersetapiclient.charts.query_context import QueryContext, PieQueryContext
from supersetapiclient.charts.types import ChartType, FilterOperationType, FilterClausesType, FilterExpressionType, \
    DatasourceType
from supersetapiclient.dashboards.itemposition import Position
from supersetapiclient.dashboards.nodeposisition import RowNodePosition
from supersetapiclient.exceptions import NotFound, ChartValidationError
from supersetapiclient.utils import remove_fields_optional


@dataclass
class Chart(Object):
    JSON_FIELDS = []

    slice_name: str

    viz_type: ChartType = None
    # _dashboards: List[Dashboard] = field(default_factory=list, init=False, repr=False)

    #For post charts, optional fields are not used.
    id: Optional[int] = None
    description: str = default_string()

    slice_name_override: Optional[str] = default_string()
    show_title: Optional[str] = default_string(default="Show Slice")
    cache_timeout: Optional[int] = field(default=None)
    result_format: Optional[str] = field(default='json')
    result_type: Optional[str] = field(default='full')

    params: Optional[Option] = field(default_factory=Option)
    query_context: Optional[QueryContext] = field(default_factory=QueryContext)

    datasource_id: str = default_string(default=None)
    datasource_type: DatasourceType = DatasourceType.TABLE

    def __post_init__(self):
        from supersetapiclient.dashboards.dashboards import Dashboard
        self._dashboards = Dashboard(dashboard_title='')

    @classmethod
    def _get_type(self, data):
        return data['viz_type']

    @property
    def dashboard(self):
        if self._dashboards:
            return self._dashboards[0]
        return None

    @property
    def dashboards(self):
        return self._dashboards

    def get_show_columns(self, prefix=None) -> list:
        if prefix is None:
            return self._extra_fields.get('show_columns', [])
        columns = []
        for column_name in self._extra_fields.get('show_columns', []):
            if prefix in column_name:
                columns.append(column_name.split('.')[-1])
        return columns

    @property
    def label_columns(self, prefix=None) -> dict:
        if prefix is None:
            return self._extra_fields.get('label_columns', {})

    @property
    def description_columns(self, prefix=None) -> dict:
        if prefix is None:
            return self._extra_fields.get('description_columns', {})

    def clone(self, slice_name:str = None, slice_name_override:str = None, dashboard_position:Position = None, clear_filter:bool = True) -> Self:
        new_chart = copy.deepcopy(self)
        new_chart.slice_name = slice_name or f'{new_chart.slice_name}_clone'
        new_chart.slice_name_override = slice_name_override or f'Chart clone de {new_chart.slice_name}'
        new_chart.id = 0

        if clear_filter:
            new_chart.clear_filter()

        # Observações sobre clonagem de gráfico
        # Se houver alteração nas configurações do gráfico, deve-se
        # - inluir um novo item em chart_configuration
        # - chartsInScope deve apontar para o id do chart original
        # - incluir um novo item em global_chart_configuration.chartsInScope
        # Se houver alterações na fonte de dados, deve-se:
        # - definir params.slice_id = novo id
        # - definir params.query_context.form_data.slice_id = novo id
        # Se a fonte de dados permanecer a mesma, deve-se
        # - manter self.params
        # - manter self.query_context


        # Observação sobre criação de novo gráfico
        # Ao criar um novo gráfico, sem está associado a um dashboard, deve-se
        # - Definir "slice_name": "aai_20231_19_899",
        # - Definir  "viz_type": "pie",
        # - Definir "datasource_id": 24,
        # - Definir "datasource_type": "table",
        # - Definir self.query_context
        # - Definir self.params
        # - Definir self.dashboards = []
        # - Remover self.id
        # - Remover self.params.slice_ide
        # - Remover self.dashboards = {}
        # - Remover self.label_columns
        # - remover self.description_columns
        # - remover self.show_title
        # - remover sel.tags
        # - remover self.thumbnail_url
        # - remover self.url
        # - remover self.viz_type
        # - remover self.cache_timeout
        # - remover self.show_columns
        return new_chart

    def clear_filter(self) -> None:
        self.params.adhoc_filters = []
        for query in self.query_context.queries:
            query.filters = []

        self.query_context.form_data.adhoc_filters = []

    def add_simple_filter(self, column_name:str,
                   value: str,
                   operator:FilterOperationType = FilterOperationType.EQUAL,
                   clause:FilterClausesType = FilterClausesType.WHERE) -> None:

        if not self.query_context.queries:
            raise ChartValidationError("""The queries list is empty. 
                        It is impossible to define the columns and metrics attributes.""")

        if len(self.query_context.queries) > 1:
            raise ChartValidationError("""There are more than one query in the queries list. 
                                       We don't know which one to include the filter in.""")

        adhoc_filter_clause = AdhocFilterClause(comparator=value,
                                                subject=column_name,
                                                clause=clause,
                                                operator=operator,
                                                expressionType=FilterExpressionType.SIMPLE)

        self.params.adhoc_filters.append(adhoc_filter_clause)
        self.query_context.form_data.adhoc_filters.append(adhoc_filter_clause)

        query_filter_clause = QueryFilterClause(col=column_name, val=value, op=operator)
        self.query_context.queries[0].filters.append(query_filter_clause)

    def to_dict(self, columns=None):
        data = super().to_dict(columns)
        if data.get('id'):
            data['id'] = data['id']

        data['params'] = self.params.to_dict()
        data['query_context'] = self.query_context.to_dict()

        dashboards = []
        data['extra_fields'] = self.extra_fields

        # for dashboard in self._dashboards:
        #     dashboard_dict = dashboard.to_dict()
        #     dashboard_data = {}
        #     columns = self.get_show_columns(prefix='dashboard')
        #     for column in columns:
        #         dashboard_data[column] = dashboard_dict[column]
        #     dashboards.append(dashboard_data)
        # data['dashboards'] = dashboards

        return data

    @remove_fields_optional
    def to_json(self, columns=None):
        data = super().to_json(columns)
        data['dashboards'] = self.params.dashboards
        data['params'] = self.params.to_json()
        data['query_context'] = self.query_context.to_json()

        if data.get('_dashboards') is not None:
            data.pop('_dashboards')

        return data

    @classmethod
    def from_json(cls, data: dict):
        from supersetapiclient.dashboards.dashboards import Dashboard

        obj = super().from_json(data)
        obj.id = data['id']

        type_ = cls._get_type(data)
        OptionClass = Option.get_class(type_)
        obj.params = OptionClass.from_json(json.loads(data['params']))

        QueryContextClass = QueryContext.get_class(type_)
        obj.query_context = QueryContextClass.from_json(json.loads(data['query_context']))

        dashboards = []
        for dashboard in obj.extra_fields.get('dashboards', []):
            dashboards.append(Dashboard.from_json(dashboard))
        obj._dashboards = dashboards

        #set default datasource
        datasource = obj.query_context.datasource
        if datasource:
            obj.datasource_id = datasource.id
            obj.datasource_type = datasource.type

        return obj



class Charts(ObjectFactories):
    endpoint = "chart/"
    base_object = Chart

    def get_chart_data(self, slice_id:str, dashboard_id: int) -> dict:
        chart = self.client.charts.get(slice_id)
        dashboard_exists = False
        for id in chart.params.dashboards:
            if dashboard_id == id:
                dashboard_exists = True
        if not dashboard_exists:
            raise NotFound(f'Dashboard id {dashboard_id} does not exist.')


        #'http://localhost:8088/api/v1/chart/data?form_data=%7B%22slice_id%22%3A347%7D&dashboard_id=12&force'
        breakpoint()
        query = {
            "slice_id": slice_id,
            "dashboard_id": dashboard_id,
            "force": None
        }
        params = {"data": json.dumps(query)}
        payload = {
            'datasource': chart.query_context.datasource.to_json(),
            'force': chart.force,
            'queries': chart.query_context.queries.to_json(),
            'form_data': chart.query_context.form_data.to_json(),
            'result_format':chart.result_format,
            'result_type': chart.result_type
        }

        response = self.client.get(self.base_url,
                                   params=params,
                                   json=payload)

        raise_for_status(response)
        return response.json().result('result')

    def add(self, chart) -> int:
        id = super().add(chart)
        chart.id = id

        if chart.dashboard:
            dashboard = self.client.dashboards.get(chart.dashboard.id)
            grid = dashboard.position.tree.grid
            node_position = grid.children[-1]

            if not isinstance(node_position, RowNodePosition):
                node_position = grid
            # from pprint import pprint
            # pprint(dashboard.to_dict())
            # breakpoint()
            dashboard.position.add_chart(chart, node_position)
            dashboard.save()


        return id


@dataclass
class PieChart(Chart):
    viz_type: ChartType = ChartType.PIE
    params: PieOption = field(default_factory=PieOption)
    query_context: PieQueryContext = field(default_factory=PieQueryContext)
