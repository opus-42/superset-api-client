"""Base classes."""
import dataclasses
import json


def json_field():
    return dataclasses.field(default=None, repr=False)

def default_string():
    default_string = dataclasses.field(default="", repr=False)


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
        return cls(**{k:v for k,v in json.items() if k in field_names})

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

        reponse = self._parent.client.put(self.base_url, json=o)
        reponse.raise_for_status()


class ObjectFactories:

    def __init__(self, client):
        """Create a new Dashboards endpoint.

        Args:
            client (client): superset client
        """
        self.client = client

        # Get infos
        response = client.get(client.join_urls(
            self.base_url,
            "_info"
        ))
        infos = response.json()
        self.edit_columns = [
            e.get("name")
            for e in infos.get("edit_columns")
        ]

    @property
    def base_url(self):
        """Base url for these objects."""
        return self.client.join_urls(
            self.client.base_url,
            self.endpoint
        )

    def find(self, **kwargs):
        """Find and get objects from api."""
        url = self.base_url

        # Get response
        query = {
            "filters": [
                {
                    "col": k,
                    "opr": "eq",
                    "value": v
                } for k, v in kwargs.items()
            ]
        }
        print(query)
        response = self.client.get(
            url,
            params={
                "q": json.dumps(query)
            }
        )
        response.raise_for_status()
        response = response.json()

        objects = []
        for r in response.get("result"):
            o = self.base_object.from_json(r)
            o._parent = self
            objects.append(o)

        return objects
