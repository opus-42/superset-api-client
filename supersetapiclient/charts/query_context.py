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


@dataclass
class FormData(Option):
    pass

@dataclass
class PieFormData(PieOption):
    pass


@dataclass
class QueryContext(Object):
    datasource: DataSource = field(default_factory=DataSource)
    queries: List[Querie] = field(default_factory=list)
    form_data: FormData = field(default_factory=FormData)
    force: bool = field(default=False)


@dataclass
class PieQueryContext(QueryContext):
    form_data: PieFormData = field(default_factory=FormData)

    @classmethod
    def get_default(cls):
        breakpoint()
