"""Base classes."""
import logging
import dataclasses
import json

from requests import Response

from supersetapiclient.exceptions import NotFound

logger = logging.getLogger(__name__)


def json_field():
    return dataclasses.field(default=None, repr=False)


def default_string():
    return dataclasses.field(default="", repr=False)


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
        return set(
            f.name
            for f in dataclasses.fields(cls)
        )

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

    def __post_init__(self):
        for f in self.JSON_FIELDS:
            setattr(self, f, json.loads(getattr(self, f) or "{}"))

    @property
    def base_url(self) -> str:
        return self._parent.client.join_urls(
            self._parent.base_url,
            str(self.id)
        )

    def fetch(self) -> None:
        """Fetch additional object information."""
        field_names = self.field_names()

        client = self._parent.client
        reponse = client.get(self.base_url)
        o = reponse.json()
        o = o.get("result")
        for k, v in o.items():
            if k in field_names:
                setattr(self, k, v)

    def save(self) -> None:
        """Save object information."""
        o = {}
        for c in self._parent.edit_columns:
            if hasattr(self, c):
                value = getattr(self, c)

                if c in self.JSON_FIELDS:
                    value = json.dumps(value)
                o[c] = value

        response = self._parent.client.put(self.base_url, json=o)
        if response.status_code in [400, 422]:
            logger.error(response.text)
        response.raise_for_status()


class ObjectFactories:
    endpoint = ""
    base_object = None

    _INFO_QUERY = {
        "keys": [
            "add_columns",
            "edit_columns"
        ]
    }

    def __init__(self, client):
        """Create a new Dashboards endpoint.

        Args:
            client (client): superset client
        """
        self.client = client

        # Get infos
        response = client.get(
            client.join_urls(
                self.base_url,
                "_info",
            ),
            params={
                "q": json.dumps(self._INFO_QUERY)
            })

        if response.status_code != 200:
            logger.error(f"Unable to build object factory for {self.endpoint}")
            response.raise_for_status()

        infos = response.json()
        self.edit_columns = [
            e.get("name")
            for e in infos.get("edit_columns", [])
        ]
        self.add_columns = [
            e.get("name")
            for e in infos.get("add_columns", [])
        ]

    @property
    def base_url(self):
        """Base url for these objects."""
        return self.client.join_urls(
            self.client.base_url,
            self.endpoint,
        )

    @staticmethod
    def _handle_reponse_status(response: Response) -> None:
        """Handle response status."""
        if response.status_code not in (200, 201):
            logger.error(
                f"Unable to proceed, API return {response.status_code}"
            )
            logger.error(f"Full API response is {response.text}")

        # Finally raising for status
        response.raise_for_status()

    def get(self, id: int):
        """Get an object by id."""
        url = self.base_url + str(id)
        response = self.client.get(
            url
        )
        response.raise_for_status()
        response = response.json()

        object_json = response.get("result")
        object_json["id"] = id
        object = self.base_object.from_json(object_json)
        object._parent = self

        return object

    def find(self, **kwargs):
        """Find and get objects from api."""
        url = self.base_url

        # Get response
        if kwargs != {}:
            query = {
                "filters": [
                    {
                        "col": k,
                        "opr": "eq",
                        "value": v
                    } for k, v in kwargs.items()
                ]
            }
            params = {
                "q": json.dumps(query)
            }
        else:
            params = {}
        response = self.client.get(
            url,
            params=params
        )
        response.raise_for_status()
        response = response.json()

        objects = []
        for r in response.get("result"):
            o = self.base_object.from_json(r)
            o._parent = self
            objects.append(o)

        return objects

    def find_one(self, **kwargs):
        """Find only object or raise an Exception."""
        objects = self.find(**kwargs)
        if len(objects) == 0:
            raise NotFound(f"No {self.base_object.__name__} has been found.")
        return objects[0]

    def add(self, obj) -> int:
        """Create a object on remote."""

        o = {}
        for c in self.add_columns:
            if hasattr(obj, c):
                value = getattr(obj, c)

                if c in obj.JSON_FIELDS:
                    value = json.dumps(value)
                o[c] = value

        response = self.client.post(self.base_url, json=o)
        response.raise_for_status()
        return response.json().get("id")
