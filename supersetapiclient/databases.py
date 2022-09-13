"""Databases."""
from dataclasses import dataclass
from typing import Optional

from supersetapiclient.base import (
    Object, ObjectFactories, default_string
)


@dataclass
class Database(Object):
    database_name: str
    id: Optional[int] = None
    allow_ctas: bool = True
    allow_cvas: bool = True
    allow_dml: bool = True
    allow_multi_schema_metadata_fetch: bool = True
    allow_run_async: bool = True
    expose_in_sqllab: bool = True
    cache_timeout: Optional[int] = None
    encrypted_extra: str = default_string()
    engine: str = default_string()
    extra: str = default_string()
    force_ctas_schema: str = default_string()
    server_cert: str = default_string()
    sqlalchemy_uri: str = default_string()

    def run(self, query, query_limit=None):
        return self._parent.client.run(
            database_id=self.id, query=query, query_limit=query_limit
        )

    def test_connection(self):
        return self._parent.test_connection(self)


class Databases(ObjectFactories):
    endpoint = "/database/"
    base_object = Database

    @property
    def test_connection_url(self):
        """Base url for these objects."""
        return self.client.join_urls(
            self.client.base_url,
            self.endpoint,
            "test_connection"
        )

    def test_connection(self, obj):
        """Test connection to a database"""
        url = self.test_connection_url
        connection_columns = ['database_name', 'sqlalchemy_uri']
        o = {c: getattr(obj, c) for c in connection_columns}
        response = self.client.post(url, json=o)
        return response.json().get('message') == 'OK'
