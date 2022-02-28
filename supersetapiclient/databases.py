"""Databases."""
from dataclasses import dataclass

from supersetapiclient.base import (
    Object, ObjectFactories, json_field, default_string
)


@dataclass
class Database(Object):
    JSON_FIELDS = ["metadata_cache_timeout"]

    id: int
    database_name: str
    allow_ctas: bool
    allow_cvas: bool
    allow_dml: bool
    allow_multi_schema_metadata_fetch: bool
    allow_run_async: bool
    metadata_cache_timeout: dict = json_field()
    encrypted_extra: str = default_string()
    engine: str = default_string()
    extra: str = json_field()
    force_ctas_schema: str = default_string()
    server_cert: str = default_string()
    sqlalchemy_uri: str = default_string()


class Databases(ObjectFactories):
    endpoint = "/database/"
    base_object = Database
