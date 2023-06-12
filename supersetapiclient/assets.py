"""Assets."""
import json
from pathlib import Path
from typing import Union

from supersetapiclient.base import raise_for_status


class Assets:
    endpoint = "assets/"

    def __init__(self, client):
        self.client = client

    @property
    def base_url(self):
        """Base url for these objects."""
        return self.client.join_urls(self.client.base_url, self.endpoint)

    @property
    def import_url(self):
        return self.client.join_urls(self.base_url, "import/")

    @property
    def export_url(self):
        return self.client.join_urls(self.base_url, "export/")

    def export(self, path: Union[Path, str]) -> None:
        """Export object into an importable file"""
        response = self.client.get(self.export_url)
        raise_for_status(response)

        content_type = response.headers["content-type"].strip()
        if content_type.startswith("application/zip"):
            data = response.content
            with open(path, "wb") as f:
                f.write(data)
            return
        raise ValueError(f"Unknown content type {content_type}")

    def import_file(self, file_path, passwords=None) -> bool:
        """Import a file on remote.

        :param file_path: Path to a JSON or ZIP file containing the import data
        :param passwords: JSON map of passwords for each featured database in
        the file. If the ZIP includes a database config in the path
        databases/MyDatabase.yaml, the password should be provided in the
        following format: {"MyDatabase": "my_password"}
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return False
        file_ext = file_path.suffix.replace(".", "")
        passwords = {f"databases/{db}.yaml": pwd for db, pwd in (passwords or {}).items()}

        files = {
            "bundle": (file_path.name, open(file_path.name, "rb"), f"application/{file_ext}"),
            "passwords": json.dumps(passwords),
        }
        response = self.client.post(self.import_url, files=files)
        raise_for_status(response)

        # If import is successful, the following is returned: {'message': 'OK'}
        return response.json().get("message") == "OK"
