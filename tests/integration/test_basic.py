import random
import string

import pytest

from supersetapiclient.charts import Chart
from supersetapiclient.dashboards import Dashboard
from supersetapiclient.databases import Database
from supersetapiclient.datasets import Dataset
from supersetapiclient.exceptions import BadRequestError
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
def dataset(superset_api, database):
    schema, table_name = random_str(8, lowercase=True), random_str(8, lowercase=True)
    database.run(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    database.run(f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} (i integer)")
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
def saved_query(superset_api, database):
    schema, table_name = random_str(8, lowercase=True), random_str(8, lowercase=True)
    database.run(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    database.run(f"CREATE TABLE IF NOT EXISTS {schema}.{table_name} (i integer)")
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


class TestClient:
    def test_databases(self, superset_api, database):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.databases.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(database.id, int)
        assert superset_api.databases.get(id=database.id).database_name == database.database_name

        # Test creating a conflicting item
        db_id, database.id = database.id, None
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.databases.add(database)
        database.id = db_id
        assert exc_info.value.response.status_code == 422
        assert exc_info.value.message == {"database_name": "A database with the same name already exists."}

        # Test connection to DB
        assert database.test_connection()

        # Test running SQL
        assert database.run("CREATE SCHEMA IF NOT EXISTS test_schema") == ([], [])

        # Test updating the item
        database.database_name = "XXX"
        database.save()
        assert superset_api.databases.get(id=database.id).database_name == "XXX"

        # Test exporting and importing the item
        file = f"/tmp/database_{database.id}.zip"
        database.export(file)
        superset_api.databases.import_file(file, overwrite=True)

        # Test deleting the item
        database.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            database.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_datasets(self, superset_api, database, dataset):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.datasets.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(dataset.id, int)
        assert superset_api.datasets.get(id=dataset.id).schema == dataset.schema
        assert superset_api.datasets.get(id=dataset.id).table_name == dataset.table_name

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
        file = f"/tmp/dataset_{dataset.id}.zip"
        dataset.export(file)
        superset_api.datasets.import_file(file, overwrite=True)

        # Test deleting the item
        dataset.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            dataset.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        # TODO: test virtual dataset

    def test_saved_queries(self, superset_api, saved_query):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.saved_queries.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(saved_query.id, int)
        assert superset_api.saved_queries.get(id=saved_query.id).schema == saved_query.schema
        assert superset_api.saved_queries.get(id=saved_query.id).label == saved_query.label

        # Conflicting saved queries can apparently not be created

        # Test running SQL
        assert saved_query.run() == ([], [])
        table_path = saved_query.sql.split("FROM")[-1].strip()  # Hacky, but it's the only way we can get the table name
        superset_api.run(
            database_id=saved_query.db_id,
            query=f"INSERT INTO {table_path} (i) VALUES (1), (2), (3)"
        )
        assert saved_query.run() == (
            [{'is_dttm': False, 'name': 'i', 'type': 'INTEGER'}],
            [{'i': 1}, {'i': 2}, {'i': 3}],
        )

        # Test updating the item
        saved_query.label = "XXX"
        saved_query.save()
        assert superset_api.saved_queries.get(id=saved_query.id).label == "XXX"

        # Test exporting and importing the item
        file = f"/tmp/saved_query_{saved_query.id}.zip"
        saved_query.export(file)
        superset_api.saved_queries.import_file(file, overwrite=True)

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

        # Conflicting charts can apparently not be created

        # Test updating the item
        chart.slice_name = "XXX"
        chart.save()
        assert superset_api.charts.get(id=chart.id).slice_name == "XXX"

        # Test exporting and importing the item
        file = f"/tmp/chart_{chart.id}.zip"
        chart.export(file)
        superset_api.charts.import_file(file, overwrite=True)

        # Test deleting the item
        chart.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            chart.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_dashboards(self, superset_api, dashboard):
        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.dashboards.get(id=0)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        assert isinstance(dashboard.id, int)
        assert superset_api.dashboards.get(id=dashboard.id).dashboard_title == dashboard.dashboard_title

        # Test creating a conflicting item
        d_id, dashboard.id = dashboard.id, None
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.dashboards.add(dashboard)
        dashboard.id = d_id
        assert exc_info.value.response.status_code == 422
        assert exc_info.value.message == {'slug': ['Must be unique']}

        # Test updating the item
        dashboard.dashboard_title = "XXX"
        dashboard.save()
        assert superset_api.dashboards.get(id=dashboard.id).dashboard_title == "XXX"

        # Test exporting and importing the item
        file = f"/tmp/dashboard_{dashboard.id}.zip"
        dashboard.export(file)
        superset_api.dashboards.import_file(file, overwrite=True)

        # Test deleting the item
        dashboard.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            dashboard.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"
