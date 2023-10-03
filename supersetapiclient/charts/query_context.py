import json
from dataclasses import dataclass, field
from typing import Optional, List

from supersetapiclient.base.base import Object
from supersetapiclient.charts.options import Option, PieOption
from supersetapiclient.charts.queries import Querie
from supersetapiclient.charts.types import DatasourceType

@dataclass
class DataSource(Object):
    id: Optional[int] = None
    type: DatasourceType = DatasourceType.TABLE


class FormData(Option):
    pass

class PieFormData(PieOption):
    pass


@dataclass
class QueryContext(Object):
    datasource: DataSource = field(default_factory=DataSource)
    queries: List[Querie] = field(default_factory=list)
    form_data: FormData = field(default_factory=FormData)
    force: bool = field(default=False)

    def queries_to_dict(self):
        queries = []
        for query in self.queries:
            queries.append(query.to_dict())
        return queries

    def queries_to_json(self):
        queries = []
        for query in self.queries:
            queries.append(query.to_json())
        return queries


    def to_dict(self, columns=None):
        data = super().to_dict(columns)
        data['queries'] = self.queries_to_dict()
        data['datasource'] = self.datasource.to_dict()
        data['form_data'] = self.form_data.to_dict()
        return data

    def to_json(self, columns=None):
        data = super().to_json(columns)
        # data['datasource'] = self.datasource.to_json()
        # data['form_data'] = self.form_data.to_json()
        # data['queries'] =self.queries_to_json()
        return json.dumps(data)

    @classmethod
    def from_json(cls, data: dict):
        obj = super().from_json(data)

        form_data = data['form_data']

        FormClass = FormData.get_class(form_data['viz_type'])
        obj.form_data = FormClass.from_json(form_data)

        obj.datasource = DataSource.from_json(data['datasource'])

        queries = []
        for query in data['queries']:
            queries.append(Querie.from_json(query))
        obj.queries = queries
        return obj


@dataclass
class PieQueryContext(QueryContext):
    form_data: PieFormData = field(default_factory=FormData)
