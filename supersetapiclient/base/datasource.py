from dataclasses import dataclass

from supersetapiclient.base.base import Object
from supersetapiclient.base.types import DatasourceType


@dataclass
class DataSource(Object):
    id: int = None
    type: DatasourceType = DatasourceType.TABLE