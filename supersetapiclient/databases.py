"""Dashboards."""
from typing import List

from dataclasses import dataclass

from supersetapiclient.base import (
    Object, ObjectFactories, json_field, default_string
)


@dataclass
class Database(Object):
    JSON_FIELDS = ["metadata_cache_timeout"]
    
    id: int
    database_name: str
    allow_csv_upload: bool
    allow_csv_upload: bool
    allow_ctas: bool
    allow_cvas: bool
    allow_dml: bool
    allow_multi_schema_metadata_fetch: bool
    allow_run_async: bool
    metadata_cache_timeout: dict = json_field()
    #configuration_method: str = default_string() ///Seems to cause errors and isn't required.
    encrypted_extra: str = default_string()
    engine: str = default_string()
    #expose_in_sqllab: bool   ///TypeError: non-default argument 'expose_in_sqllab' follows default argument
    extra: str = json_field()
    force_ctas_schema: str = default_string()
    #impersonate_user: bool  ///non-default argument
    server_cert: str = default_string()
    sqlalchemy_uri: str = default_string()

    
        
class Databases(ObjectFactories):
    endpoint = "/database/"
    base_object = Database
