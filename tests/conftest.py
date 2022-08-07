"""Fixture and superset app for testing."""
import json
from pathlib import Path

import pytest
import requests_mock

from supersetapiclient.client import SupersetClient

# Testing configuration
SUPERSET_HOST = "localhost"
SUPERSET_BASE_URI = f"http://{SUPERSET_HOST}"
SUPERSET_API_URI = f"{SUPERSET_BASE_URI}/api/v1"
API_MOCKS = Path(__file__).parent / "mocks" / "endpoints"


@pytest.fixture
def permanent_requests(requests_mock):

    # List domain in folder
    for domain in API_MOCKS.iterdir():
        domain_name = domain.name

        if domain.is_dir():

            # List file in dir
            for endpoint in domain.iterdir():
                if endpoint.is_file():

                    endpoint_name, action = endpoint.name.split(".")

                    # Register mock on action within domain and endpoint
                    api_url = f"{SUPERSET_API_URI}/{domain_name}/{endpoint_name}"
                    getattr(requests_mock, action)(
                        url=api_url,
                        json=json.load(endpoint.open())
                    )
                    getattr(requests_mock, action)(
                        url=f"{api_url}/",
                        json=json.load(endpoint.open())
                    )

@pytest.fixture
def client(permanent_requests):

    client = SupersetClient(
        SUPERSET_BASE_URI,
        "test",
        "test"
    )
    yield client

