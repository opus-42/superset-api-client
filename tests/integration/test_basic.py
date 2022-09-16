import json
import random
import string
import tempfile

import pytest
import requests
import requests.exceptions

from supersetapiclient.charts import Chart
from supersetapiclient.client import SupersetClient, raise_for_status
from supersetapiclient.dashboards import Dashboard
from supersetapiclient.databases import Database
from supersetapiclient.datasets import Dataset
from supersetapiclient.exceptions import BadRequestError, ComplexBadRequestError, MultipleFound, NotFound, QueryLimitReached
from supersetapiclient.saved_queries import SavedQuery


def random_str(length, lowercase=False):
    # Create a random string
    chars = string.ascii_lowercase if lowercase else string.ascii_letters
    return "".join(random.choice(chars) for _ in range(length))


@pytest.fixture
def database(superset_api):
    db = Database(
        database_name=random_str(8),
        sqlalchemy_uri="postgresql+psycopg2://postgres:postgres@pg:5432/postgres",
    )
    superset_api.databases.add(db)
    yield db
    try:
        db.delete()
    except BadRequestError as e:
        if not (e.response.status_code == 404 and e.message == "Not found"):
            raise


@pytest.fixture
def database_with_table(database):
    schema, table_name = random_str(8, lowercase=True), random_str(8, lowercase=True)
    database.run(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    database.run(f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} (i integer)")
    yield database, schema, table_name
    database.run(f"DROP TABLE IF EXISTS {schema}.{table_name}")
    database.run(f"DROP SCHEMA IF EXISTS {schema}")


@pytest.fixture
def dataset(superset_api, database_with_table):
    database, schema, table_name = database_with_table
    ds = Dataset(
        database_id=database.id,
        schema=schema,
        table_name=table_name,
        description="My Test Table",
    )
    superset_api.datasets.add(ds)
    yield ds
    try:
        ds.delete()
    except BadRequestError as e:
        if not (e.response.status_code == 404 and e.message == "Not found"):
            raise


@pytest.fixture
def virtual_dataset(superset_api, database):
    # We're using 'dataset' and 'virtual_dataset' in the same test case so need to create a new table here because
    # two databases can't cover the same table.
    schema, table_name = random_str(8, lowercase=True), random_str(8, lowercase=True)
    database.run(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    database.run(f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} (i integer)")
    ds = Dataset(
        database_id=database.id,
        schema=schema,
        table_name=table_name,
        description="My Virtual Table",
        sql=f"SELECT i FROM {schema}.{table_name} ORDER BY i LIMIT 3",
    )
    superset_api.datasets.add(ds)
    yield ds
    database.run(f"DROP TABLE IF EXISTS {schema}.{table_name}")
    database.run(f"DROP SCHEMA IF EXISTS {schema}")
    try:
        ds.delete()
    except BadRequestError as e:
        if not (e.response.status_code == 404 and e.message == "Not found"):
            raise


@pytest.fixture
def saved_query(superset_api, database_with_table):
    database, schema, table_name = database_with_table
    sq = SavedQuery(
        db_id=database.id,
        label=random_str(8),
        schema=schema,
        sql=f"SELECT i FROM {schema}.{table_name}",
    )
    superset_api.saved_queries.add(sq)
    yield sq
    try:
        sq.delete()
    except BadRequestError as e:
        if not (e.response.status_code == 404 and e.message == "Not found"):
            raise


@pytest.fixture
def chart(superset_api, dataset):
    c = Chart(
        datasource_id=dataset.id,
        datasource_type="table",
        slice_name=random_str(8),
        viz_type="table",
    )
    superset_api.charts.add(c)
    yield c
    try:
        c.delete()
    except BadRequestError as e:
        if not (e.response.status_code == 404 and e.message == "Not found"):
            raise


@pytest.fixture
def dashboard(superset_api, dataset):
    d = Dashboard(
        dashboard_title=random_str(8),
        published=True,
        slug=random_str(8),
    )
    superset_api.dashboards.add(d)
    yield d
    try:
        d.delete()
    except BadRequestError as e:
        if not (e.response.status_code == 404 and e.message == "Not found"):
            raise


class TestEntities:
    def test_databases(self, superset_api, database):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.databases.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(database.id, int)
        assert superset_api.databases.get(id=database.id).database_name == database.database_name

        # Test fetch
        database.fetch()

        # Test count
        assert superset_api.databases.count() >= 1

        # Test creating a conflicting item
        db_id, database.id = database.id, None
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.databases.add(database)
        database.id = db_id
        assert exc_info.value.response.status_code == 422
        assert exc_info.value.message == {"database_name": "A database with the same name already exists."}
        assert (
            str(exc_info.value)
            == """\
{
    "database_name": "A database with the same name already exists."
}"""
        )

        # Test connection to DB
        assert database.test_connection()

        # Test running SQL
        schema = random_str(8)
        try:
            assert database.run(f"CREATE SCHEMA IF NOT EXISTS {schema}") == ([], [])
        finally:
            database.run(f"DROP SCHEMA IF EXISTS {schema}")

        # Test running invalid SQL
        with pytest.raises(ComplexBadRequestError) as exc_info:
            database.run("DROP SCHEMA xxx")
        assert exc_info.value.response.status_code == 400
        assert (
            str(exc_info.value)
            == """\
[
    {
        "message": "postgresql error: schema \\"xxx\\" does not exist\\n",
        "error_type": "GENERIC_DB_ENGINE_ERROR",
        "extra": {
            "engine_name": "PostgreSQL",
            "issue_codes": [
                {
                    "code": 1002,
                    "message": "Issue 1002 - The database returned an unexpected error."
                }
            ]
        }
    }
]"""
        )

        # Test updating the item
        database.database_name = "XXX"
        database.save()
        assert superset_api.databases.get(id=database.id).database_name == "XXX"

        # Test exporting and importing the item
        with tempfile.NamedTemporaryFile(suffix=".zip") as f:
            database.export(f.name)
            superset_api.databases.import_file(f.name, overwrite=True)

        # Test deleting the item
        database.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            database.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_datasets(self, superset_api, dataset, virtual_dataset):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.datasets.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(dataset.id, int)
        assert superset_api.datasets.get(id=dataset.id).schema == dataset.schema
        assert superset_api.datasets.get(id=dataset.id).table_name == dataset.table_name

        # Test fetch
        dataset.fetch()

        # Test count
        assert superset_api.datasets.count() >= 1

        # Test creating a conflicting item
        ds_id, dataset.id = dataset.id, None
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.datasets.add(dataset)
        dataset.id = ds_id
        assert exc_info.value.response.status_code == 422
        assert exc_info.value.message == {"table_name": [f"Dataset {dataset.table_name} already exists"]}

        # Test running SQL
        with pytest.raises(ValueError) as exc_info:
            dataset.run()
        assert exc_info.value.args[0] == "Cannot run a dataset with no SQL"

        # Test updating the item
        dataset.table_name = "XXX"
        dataset.save()
        assert superset_api.datasets.get(id=dataset.id).table_name == "XXX"

        # Test exporting and importing the item
        with tempfile.NamedTemporaryFile(suffix=".zip") as f:
            dataset.export(f.name)
            superset_api.datasets.import_file(f.name, overwrite=True)

        # Test deleting the item
        dataset.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            dataset.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        # Test virtual dataset
        assert virtual_dataset.run() == ([], [])
        # Insert more values than the query limit defined in superset_config.py::SqlExecuteRestApi.query_limit
        values = ", ".join(f"({i})" for i in range(1, 21))
        superset_api.run(
            database_id=virtual_dataset.database_id,
            query=f"INSERT INTO {virtual_dataset.schema}.{virtual_dataset.table_name} (i) VALUES {values}",
        )
        # We're getting results limited by the LIMIT value in virtual_dataset.sql
        assert virtual_dataset.run() == (
            [{"is_dttm": False, "name": "i", "type": "INTEGER"}],
            [{"i": 1}, {"i": 2}, {"i": 3}],
        )
        # Limit the query result size. TODO: This doesn't actually work in Superset 2.x for some reason
        assert virtual_dataset.run(query_limit=2) == (
            [{"is_dttm": False, "name": "i", "type": "INTEGER"}],
            [{"i": 1}, {"i": 2}, {"i": 3}],
        )
        virtual_dataset.sql = f"SELECT i FROM {virtual_dataset.schema}.{virtual_dataset.table_name} ORDER BY i LIMIT 15"
        # We're hitting the query limit defined in superset_config.py::SqlExecuteRestApi.query_limit
        with pytest.raises(QueryLimitReached) as exc_info:
            virtual_dataset.run()
        assert (
            exc_info.value.args[0]
            == "You have exceeded the maximum number of rows that can be returned (10). Either set the `query_limit` "
            "attribute to a lower number than this, or add LIMIT keywords to your SQL statement to limit the "
            "number of rows returned."
        )

    def test_saved_queries(self, superset_api, saved_query):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.saved_queries.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(saved_query.id, int)
        assert superset_api.saved_queries.get(id=saved_query.id).schema == saved_query.schema
        assert superset_api.saved_queries.get(id=saved_query.id).label == saved_query.label

        # Test fetch
        saved_query.fetch()

        # Test count
        assert superset_api.saved_queries.count() >= 1

        # Conflicting saved queries can apparently not be created

        # Test running SQL
        assert saved_query.run() == ([], [])
        table_path = saved_query.sql.split("FROM")[-1].strip()  # Hacky, but it's the only way we can get the table name
        superset_api.run(
            database_id=saved_query.db_id,
            query=f"INSERT INTO {table_path} (i) VALUES (1), (2), (3)",
        )
        assert saved_query.run() == (
            [{"is_dttm": False, "name": "i", "type": "INTEGER"}],
            [{"i": 1}, {"i": 2}, {"i": 3}],
        )

        # Test updating the item
        saved_query.label = "XXX"
        saved_query.save()
        assert superset_api.saved_queries.get(id=saved_query.id).label == "XXX"

        # Test exporting and importing the item
        with tempfile.NamedTemporaryFile(suffix=".zip") as f:
            saved_query.export(f.name)
            superset_api.saved_queries.import_file(f.name, overwrite=True)

        # Test deleting the item
        saved_query.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            saved_query.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_charts(self, superset_api, chart):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.charts.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(chart.id, int)
        assert superset_api.charts.get(id=chart.id).slice_name == chart.slice_name
        assert superset_api.charts.get(id=chart.id).viz_type == chart.viz_type

        # Test fetch
        chart.fetch()

        # Test count
        assert superset_api.charts.count() >= 1

        # Conflicting charts can apparently not be created

        # Test updating the item
        chart.slice_name = "XXX"
        chart.save()
        assert superset_api.charts.get(id=chart.id).slice_name == "XXX"

        # Test exporting and importing the item
        with tempfile.NamedTemporaryFile(suffix=".zip") as f:
            chart.export(f.name)
            superset_api.charts.import_file(f.name, overwrite=True)

        # Test deleting the item
        chart.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            chart.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_dashboards(self, superset_api, dashboard, chart):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.dashboards.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(dashboard.id, int)
        assert superset_api.dashboards.get(id=dashboard.id).dashboard_title == dashboard.dashboard_title

        # Test fetch
        dashboard.fetch()

        # Test count
        assert superset_api.dashboards.count() >= 1

        # Test creating a conflicting item
        d_id, dashboard.id = dashboard.id, None
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.dashboards.add(dashboard)
        dashboard.id = d_id
        assert exc_info.value.response.status_code == 422
        assert exc_info.value.message == {"slug": ["Must be unique"]}

        # Test updating the item
        dashboard.dashboard_title = "XXX"
        dashboard.save()
        assert superset_api.dashboards.get(id=dashboard.id).dashboard_title == "XXX"

        # Test changing colors
        dashboard.update_colors({"label": "#fcba03"})
        dashboard.save()
        assert superset_api.dashboards.get(id=dashboard.id).colors == {"label": "#fcba03"}

        # Test connected charts
        chart.dashboards.append(dashboard.id)
        chart.save()
        assert [d["id"] for d in superset_api.charts.get(id=chart.id).dashboards] == [dashboard.id]
        assert [c.id for c in superset_api.dashboards.get(id=dashboard.id).get_charts()] == [chart.id]

        # Test exporting and importing the item
        with tempfile.NamedTemporaryFile(suffix=".zip") as f:
            dashboard.export(f.name)
            superset_api.dashboards.import_file(f.name, overwrite=True)

        # Test deleting the item
        dashboard.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            dashboard.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_find_one(self, superset_api):
        title = random_str(8)
        with pytest.raises(NotFound):
            superset_api.dashboards.find_one(dashboard_title=title)

        superset_api.dashboards.add(Dashboard(dashboard_title=title, published=True, slug=random_str(8)))
        assert superset_api.dashboards.find_one(dashboard_title=title).dashboard_title == title

        superset_api.dashboards.add(Dashboard(dashboard_title=title, published=True, slug=random_str(8)))
        with pytest.raises(MultipleFound):
            superset_api.dashboards.find_one(dashboard_title=title)


class TestClient:
    def test_no_verify(self, superset_url):
        superset_api = SupersetClient(superset_url, "admin", "admin", verify=False)
        assert superset_api.databases.count() >= 0  # Call something that makes an actual HTTP call

    def test_refresh_token(self, requests_mock, superset_api):
        # Mock test a token expiry message from the API
        requests_mock.real_http = True
        superset_api.databases.find()  # Call something that sets up the initial token
        url = superset_api.databases.base_url

        # HTTP 401 but no token expiry message in response
        requests_mock.get(url, status_code=401)
        r = superset_api.get(url)
        assert superset_api.token_refresher(r=r).status_code == 401

        # HTTP 401 but wrong message in response
        requests_mock.get(url, status_code=401, content=json.dumps({"msg": "XXX"}).encode())
        r = superset_api.get(url)
        assert superset_api.token_refresher(r=r).status_code == 401

        # HTTP 401 and proper token expiry message in response
        requests_mock.get(
            url,
            [
                dict(
                    status_code=401,
                    content=json.dumps({"msg": "Token has expired"}).encode(),
                ),
                dict(status_code=200, content=json.dumps([]).encode()),
            ],
        )
        r = superset_api.get(url)
        assert superset_api.token_refresher(r=r).status_code == 200

    def test_authenticate(self, monkeypatch, superset_url):
        superset_api = SupersetClient(superset_url)  # No username or password yet

        monkeypatch.setattr("getpass.getuser", lambda: "admin")
        monkeypatch.setattr("getpass.getpass", lambda: "admin")
        superset_api.authenticate()
        assert superset_api.username == "admin"
        assert superset_api._password == "admin"
        assert superset_api.password == "*****"

    def test_standard_sql_endpoint(self):
        # Test the _sql_endpoint value returned by the plain SupersetClient class. The CustomClient class used in this
        # test suite overrides it.
        superset_api = SupersetClient("https://example.com")
        assert superset_api._sql_endpoint == "https://example.com/superset/sql_json/"

    def test_export_failure(self, requests_mock, superset_api):
        requests_mock.real_http = True
        requests_mock.get(
            superset_api.databases.export_url,
            status_code=200,
            headers={"content-type": "application/x"},
        )
        with pytest.raises(ValueError) as exc_info:
            superset_api.databases.export([1], "/dev/null")
        assert exc_info.value.args[0] == "Unknown content type application/x"


class TestExceptions:
    def test_raise_for_status(self, requests_mock):
        url = "https://example.com"

        requests_mock.get(url, status_code=500, content=b"XXX")
        r = requests.get(url)
        with pytest.raises(requests.exceptions.HTTPError):
            raise_for_status(r)

        requests_mock.get(url, status_code=500, content=json.dumps({"message": "XXX"}).encode())
        r = requests.get(url)
        with pytest.raises(BadRequestError) as exc_info:
            raise_for_status(r)
        assert exc_info.value.message == "XXX"

        requests_mock.get(url, status_code=500, content=json.dumps({"errors": ["foo"]}).encode())
        r = requests.get(url)
        with pytest.raises(ComplexBadRequestError) as exc_info:
            raise_for_status(r)
        assert exc_info.value.errors == ["foo"]
