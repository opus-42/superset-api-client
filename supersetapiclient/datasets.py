"""Dashboards."""
from dataclasses import dataclass, field
from typing import Optional

from supersetapiclient.base import Object, ObjectFactories


@dataclass
class Dataset(Object):
    JSON_FIELDS = []

    id: Optional[int] = None
    table_name: str = ""
    schema: str = ""
    columns: list = field(default_factory=list)
    description: str = ""
    kind: str = ""
    database_id: Optional[int] = None
    sql: str = ""

    @classmethod
    def from_json(cls, json: dict):
        res = super().from_json(json)
        database = json.get("database")
        if database:
            res.database_id = database.get("id")
        return res

    def to_json(self, *args, **kwargs):
        o = super().to_json(*args, **kwargs)
        o.pop("columns", None)
        if self.id:
            o["database_id"] = self.database_id
        else:
            o["database"] = self.database_id
        return o

    def run(self, query_limit=None):
        if not self.sql:
            raise ValueError("Cannot run a dataset with no SQL")
        return self._parent.client.run(database_id=self.database_id, query=self.sql, query_limit=query_limit)


class Datasets(ObjectFactories):
    endpoint = "dataset/"
    base_object = Dataset
