"""Fixture and superset app for testing."""
from functools import partial
import os
from pathlib import Path

import pytest

from superset.app import create_app
from werkzeug import test
from supersetapiclient.client import SupersetClient

# Launch and configure local superset application
path = Path(__file__).parent / "superset_test_config.py"
os.environ["SUPERSET_CONFIG_PATH"] = str(path.resolve())


@pytest.fixture(scope="session")
def test_client():
    app = create_app()

    with app.test_client() as client:
        with app.app_context() as app_context:
            admin = app.appbuilder.sm.find_role("Admin")
            app.appbuilder.sm.add_user(
                username="test",
                first_name="test",
                last_name="test",
                email="test",
                role=admin)

            yield client


@pytest.fixture(scope="session")
def client(test_client):

    client = SupersetClient(
        "http://localhost",
        "test",
        "test"
    )

    # Patch requests
    client.get = partial(
        test_client.get,
        client._headers
    )
    client.put = partial(
        test_client.put,
        client._headers
    )
    client.post = partial(
        test_client.post,
        client._headers
    )
    client.delete = partial(
        test_client.delete,
        client._headers
    )
