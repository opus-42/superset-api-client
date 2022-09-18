"""Fixture and superset app for testing."""
import json
import os
from pathlib import Path

import pytest
import requests
import requests.exceptions
import requests_mock  # noqa

from supersetapiclient.client import SupersetClient

# Testing configuration
SUPERSET_HOST = "localhost"
SUPERSET_BASE_URI = f"https://{SUPERSET_HOST}"
SUPERSET_API_URI = f"{SUPERSET_BASE_URI}/api/v1"
API_MOCKS = Path(__file__).parent / "mocks" / "endpoints"


class CustomClient(SupersetClient):
    @property
    def _sql_endpoint(self) -> str:
        return self.join_urls(self.base_url, "execute_sql_json/")


@pytest.fixture
def permanent_requests(requests_mock):  # noqa

    # List domain in folder
    for domain in API_MOCKS.iterdir():
        domain_name = domain.name

        if domain.is_dir():

            # List file in dir
            for endpoint in domain.iterdir():
                if endpoint.is_file():

                    endpoint_name, action = endpoint.name.split(".")

                    # Register mock on action within domain and endpoint
                    url = f"{SUPERSET_API_URI}/{domain_name}/{endpoint_name}"
                    getattr(requests_mock, action)(url=url, json=json.load(endpoint.open()))
                    getattr(requests_mock, action)(url=f"{url}/", json=json.load(endpoint.open()))


@pytest.fixture
def client(permanent_requests):

    client = SupersetClient(SUPERSET_BASE_URI, "test", "test")
    yield client


def is_responsive(url):
    try:
        return requests.get(url).status_code == 200
    except requests.exceptions.ConnectionError:
        return False


@pytest.fixture(scope="session")
def superset_url(docker_ip, docker_services):
    """Ensure that Superset API is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    schema = "http"
    port = docker_services.port_for("superset", 8080)
    url = f"{schema}://{docker_ip}:{port}"
    if schema == "http":
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    docker_services.wait_until_responsive(timeout=600, pause=1.0, check=lambda: is_responsive(url))
    yield url


@pytest.fixture
def superset_api(superset_url):
    yield CustomClient(superset_url, "admin", "admin")


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return str(Path(__file__).parent.parent / "docker-compose.yml")


# Fixtures to enable testing without starting and stopping containers on each run.
# See https://github.com/avast/pytest-docker/issues/46#issuecomment-887408396
def pytest_addoption(parser):
    """Add the --keepalive option for pytest."""
    parser.addoption(
        "--keepalive",
        "-K",
        action="store_true",
        default=False,
        help="Keep Docker containers alive",
    )


@pytest.fixture(scope="session")
def keepalive(request):
    return request.config.option.keepalive


@pytest.fixture(scope="session")
def docker_compose_project_name(keepalive, docker_compose_project_name):
    if keepalive:
        return "test_superset_app"
    return docker_compose_project_name


@pytest.fixture(scope="session")
def docker_cleanup(keepalive, docker_cleanup):
    if keepalive:
        return "version"
    return docker_cleanup
