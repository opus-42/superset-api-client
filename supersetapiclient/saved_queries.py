"""Saved queries."""
from dataclasses import dataclass

from supersetapiclient.base import (
    Object, ObjectFactories, default_string
)


@dataclass
class SavedQuery(Object):
    JSON_FIELDS = []

    id: int
    label: str
    description: str = default_string()
    sql: str = default_string()
    db_id: int = None
    schema: str = default_string()

    @classmethod
    def from_json(cls, json: dict):
        res = super().from_json(json)
        if database := json.get("database"):
            res.db_id = database.get("id")
        return res


class SavedQueries(ObjectFactories):
    endpoint = "/saved_query/"
    base_object = SavedQuery
