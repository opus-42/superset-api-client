"""Base classes."""
import dataclasses
import logging

try:
    from functools import cached_property
except ImportError:  # pragma: no cover
    # Python<3.8
    from cached_property import cached_property

import json
import os.path
from pathlib import Path
from typing import List, Union

import yaml
from requests import HTTPError

from supersetapiclient.exceptions import BadRequestError, ComplexBadRequestError, MultipleFound, NotFound

logger = logging.getLogger(__name__)


def json_field():
    return dataclasses.field(default=None, repr=False)


def default_string():
    return dataclasses.field(default="", repr=False)


def raise_for_status(response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        # Attempt to propagate the server error message
        try:
            error_msg = response.json()["message"]
        except Exception:
            try:
                errors = response.json()["errors"]
            except Exception:
                raise e
            raise ComplexBadRequestError(*e.args, request=e.request, response=e.response, errors=errors) from None
        raise BadRequestError(*e.args, request=e.request, response=e.response, message=error_msg) from None


class Object:
    _parent = None
    JSON_FIELDS = []

    @classmethod
    def fields(cls):
        """Get field names."""
        return dataclasses.fields(cls)

    @classmethod
    def field_names(cls):
        """Get field names."""
        return {f.name for f in cls.fields()}

    @classmethod
    def from_json(cls, json: dict):
        """Create Object from json

        Args:
            json (dict): a dictionary

        Returns:
            Object: return the related object
        """
        field_names = cls.field_names()
        return cls(**{k: v for k, v in json.items() if k in field_names})

    def to_json(self, columns):
        o = {}
        for c in columns:
            if not hasattr(self, c):
                # Column that is not implemented yet
                continue
            value = getattr(self, c)
            if c in self.JSON_FIELDS:
                value = json.dumps(value)
            o[c] = value
        return o

    def __post_init__(self):
        for f in self.JSON_FIELDS:
            setattr(self, f, json.loads(getattr(self, f) or "{}"))

    @property
    def base_url(self) -> str:
        return self._parent.client.join_urls(self._parent.base_url, self.id)

    def export(self, path: Union[Path, str]) -> None:
        """Export object to path"""
        self._parent.export(ids=[self.id], path=path)

    def fetch(self) -> None:
        """Fetch additional object information."""
        field_names = self.field_names()

        client = self._parent.client
        response = client.get(self.base_url)
        o = response.json().get("result")
        for k, v in o.items():
            if k in field_names:
                if k in self.JSON_FIELDS:
                    setattr(self, k, json.loads(v or "{}"))
                else:
                    setattr(self, k, v)

    def save(self) -> None:
        """Save object information."""
        o = self.to_json(columns=self._parent.edit_columns)
        response = self._parent.client.put(self.base_url, json=o)
        raise_for_status(response)

    def delete(self) -> bool:
        return self._parent.delete(id=self.id)


class ObjectFactories:
    endpoint = ""
    base_object: Object = None

    _INFO_QUERY = {"keys": ["add_columns", "edit_columns"]}

    def __init__(self, client):
        """Create a new Dashboards endpoint.

        Args:
            client (client): superset client
        """
        self.client = client

    @cached_property
    def _infos(self):
        # Get infos
        response = self.client.get(self.info_url, params={"q": json.dumps(self._INFO_QUERY)})

        raise_for_status(response)
        return response.json()

    @property
    def add_columns(self):
        return [e.get("name") for e in self._infos.get("add_columns", [])]

    @property
    def edit_columns(self):
        return [e.get("name") for e in self._infos.get("edit_columns", [])]

    @property
    def base_url(self):
        """Base url for these objects."""
        return self.client.join_urls(self.client.base_url, self.endpoint)

    @property
    def info_url(self):
        return self.client.join_urls(self.base_url, "_info")

    @property
    def import_url(self):
        return self.client.join_urls(self.base_url, "import/")

    @property
    def export_url(self):
        return self.client.join_urls(self.base_url, "export/")

    def get(self, id: int):
        """Get an object by id."""
        url = self.client.join_urls(self.base_url, id)
        response = self.client.get(url)
        raise_for_status(response)
        response = response.json()

        object_json = response.get("result")
        object_json["id"] = id
        object = self.base_object.from_json(object_json)
        object._parent = self

        return object

    def find(self, page_size: int = 100, page: int = 0, **kwargs):
        """Find and get objects from api."""
        # Get response
        query = {
            "page_size": page_size,
            "page": page,
            "filters": [{"col": k, "opr": "eq", "value": v} for k, v in kwargs.items()],
        }

        params = {"q": json.dumps(query)}

        response = self.client.get(self.base_url, params=params)
        raise_for_status(response)
        response = response.json()

        objects = []
        for r in response.get("result"):
            o = self.base_object.from_json(r)
            o._parent = self
            objects.append(o)

        return objects

    def count(self):
        """Count objects."""
        response = self.client.get(self.base_url)
        raise_for_status(response)
        return response.json()["count"]

    def find_one(self, **kwargs):
        """Find only object or raise an Exception."""
        objects = self.find(**kwargs)
        if len(objects) == 0:
            raise NotFound(f"No {self.base_object.__name__} found")
        if len(objects) > 1:
            raise MultipleFound(f"Multiple {self.base_object.__name__} found")
        return objects[0]

    def add(self, obj) -> int:
        """Create an object on remote."""

        o = obj.to_json(columns=self.add_columns)
        response = self.client.post(self.base_url, json=o)
        raise_for_status(response)
        obj.id = response.json().get("id")
        obj._parent = self
        return obj.id

    def export(self, ids: List[int], path: Union[Path, str]) -> None:
        """Export object into an importable file"""
        ids_array = ",".join([str(i) for i in ids])
        response = self.client.get(self.export_url, params={"q": f"[{ids_array}]"})

        raise_for_status(response)

        content_type = response.headers["content-type"].strip()
        if content_type.startswith("application/text"):  # pragma: no cover
            # Superset 1.x
            data = yaml.load(response.text, Loader=yaml.FullLoader)
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False)
            return
        if content_type.startswith("application/json"):  # pragma: no cover
            # Superset 1.x
            data = response.json()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return
        if content_type.startswith("application/zip"):
            data = response.content
            with open(path, "wb") as f:
                f.write(data)
            return
        raise ValueError(f"Unknown content type {content_type}")

    def delete(self, id: int) -> bool:
        """Delete a object on remote."""
        url = self.client.join_urls(self.base_url, id)
        response = self.client.delete(url)
        raise_for_status(response)
        return response.json().get("message") == "OK"

    def import_file(self, file_path, overwrite=False, passwords=None) -> dict:
        """Import a file on remote.

        :param file_path: Path to a JSON or ZIP file containing the import data
        :param overwrite: If True, overwrite existing remote entities
        :param passwords: JSON map of passwords for each featured database in
        the file. If the ZIP includes a database config in the path
        databases/MyDatabase.yaml, the password should be provided in the
        following format: {"MyDatabase": "my_password"}
        """
        data = {"overwrite": json.dumps(overwrite)}
        passwords = {f"databases/{db}.yaml": pwd for db, pwd in (passwords or {}).items()}
        file_name = os.path.split(file_path)[-1]
        file_ext = os.path.splitext(file_name)[-1].lstrip(".").lower()
        with open(file_path, "rb") as f:
            files = {
                "formData": (file_name, f, f"application/{file_ext}"),
                "passwords": (None, json.dumps(passwords), None),
            }
            response = self.client.post(
                self.import_url,
                files=files,
                data=data,
                headers={"Accept": "application/json"},
            )
        raise_for_status(response)

        # If import is successful, the following is returned: {'message': 'OK'}
        return response.json().get("message") == "OK"
