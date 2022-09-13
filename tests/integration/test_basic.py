import pytest

from supersetapiclient.charts import Chart
from supersetapiclient.dashboards import Dashboard
from supersetapiclient.databases import Database
from supersetapiclient.datasets import Dataset
from supersetapiclient.exceptions import BadRequestError
from supersetapiclient.saved_queries import SavedQuery


class TestClient:
    def test_databases(self, superset_api):
        # Clean up any leftover items
        for i in superset_api.dashboards.find():
            i.delete()
        for i in superset_api.charts.find():
            i.delete()
        for i in superset_api.saved_queries.find():
            i.delete()
        for i in superset_api.datasets.find():
            i.delete()
        for i in superset_api.databases.find():
            i.delete()

        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.databases.get(id=1)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        # Test creating a new item
        db = Database(
            database_name="PostgreSQL",
            sqlalchemy_uri="postgresql+psycopg2://postgres:postgres@pg:5432/postgres",
        )
        superset_api.databases.add(db)
        assert isinstance(db.id, int)
        assert superset_api.databases.get(id=db.id).database_name == "PostgreSQL"

        # Test creating a conflicting item
        db_id, db.id = db.id, None
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.databases.add(db)
        db.id = db_id
        assert exc_info.value.response.status_code == 422
        assert exc_info.value.message == {"database_name": "A database with the same name already exists."}

        # Test connection to DB
        assert db.test_connection()

        # Test running SQL
        assert db.run("CREATE SCHEMA IF NOT EXISTS test_schema") == ([], [])

        # Test updating the item
        db.database_name = "XXX"
        db.save()
        assert superset_api.databases.get(id=db.id).database_name == "XXX"

        # Test deleting the item
        db.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            db.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_datasets(self, superset_api):
        # Clean up any leftover items
        for i in superset_api.saved_queries.find():
            i.delete()
        for i in superset_api.datasets.find():
            i.delete()
        for i in superset_api.databases.find():
            i.delete()

        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.datasets.get(id=1)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        # Test creating a new item
        db = Database(
            database_name="PostgreSQL",
            sqlalchemy_uri="postgresql+psycopg2://postgres:postgres@pg:5432/postgres",
        )
        superset_api.databases.add(db)
        db.run("CREATE SCHEMA IF NOT EXISTS test_schema")
        db.run("CREATE TABLE IF NOT EXISTS test_schema.test_table (i integer)")
        ds = Dataset(
            database_id=db.id,
            schema="test_schema",
            table_name="test_table",
            description="My Test Table",
        )
        superset_api.datasets.add(ds)
        assert isinstance(ds.id, int)
        assert superset_api.datasets.get(id=ds.id).schema == "test_schema"
        assert superset_api.datasets.get(id=ds.id).table_name == "test_table"

        # Test creating a conflicting item
        ds_id, ds.id = ds.id, None
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.datasets.add(ds)
        ds.id = ds_id
        assert exc_info.value.response.status_code == 422
        assert exc_info.value.message == {'table_name': ['Dataset test_table already exists']}

        # Test running SQL
        with pytest.raises(ValueError) as exc_info:
            ds.run()
        assert exc_info.value.args[0] == "Cannot run a dataset with no SQL"

        # Test updating the item
        ds.table_name = "XXX"
        ds.save()
        assert superset_api.datasets.get(id=ds.id).table_name == "XXX"

        # Test deleting the item
        ds.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            ds.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        # TODO: test virtual dataset

    def test_saved_queries(self, superset_api):
        # Clean up any leftover items
        for i in superset_api.saved_queries.find():
            i.delete()
        for i in superset_api.databases.find():
            i.delete()

        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.saved_queries.get(id=1)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        # Test creating a new item
        db = Database(
            database_name="PostgreSQL",
            sqlalchemy_uri="postgresql+psycopg2://postgres:postgres@pg:5432/postgres",
        )
        superset_api.databases.add(db)
        db.run("CREATE SCHEMA IF NOT EXISTS test_schema")
        db.run("CREATE TABLE IF NOT EXISTS test_schema.test_table (i integer)")
        sq = SavedQuery(
            db_id=db.id,
            label="My Test Query",
            schema="test_schema",
            sql="SELECT i FROM test_schema.test_table",
        )
        superset_api.saved_queries.add(sq)
        assert isinstance(sq.id, int)
        assert superset_api.saved_queries.get(id=sq.id).schema == "test_schema"
        assert superset_api.saved_queries.get(id=sq.id).label == "My Test Query"

        # Conflicting saved queries can apparently not be created

        # Test running SQL
        db.run("DELETE FROM test_schema.test_table")
        assert sq.run() == ([], [])
        db.run("INSERT INTO test_schema.test_table (i) VALUES (1), (2), (3)")
        assert sq.run() == (
            [{'is_dttm': False, 'name': 'i', 'type': 'INTEGER'}],
            [{'i': 1}, {'i': 2}, {'i': 3}],
        )

        # Test updating the item
        sq.label = "XXX"
        sq.save()
        assert superset_api.saved_queries.get(id=sq.id).label == "XXX"

        # Test deleting the item
        sq.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            sq.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_charts(self, superset_api):
        # Clean up any leftover items
        for i in superset_api.charts.find():
            i.delete()
        for i in superset_api.datasets.find():
            i.delete()
        for i in superset_api.databases.find():
            i.delete()

        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.charts.get(id=1)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        # Test creating a new item
        db = Database(
            database_name="PostgreSQL",
            sqlalchemy_uri="postgresql+psycopg2://postgres:postgres@pg:5432/postgres",
        )
        superset_api.databases.add(db)
        db.run("CREATE SCHEMA IF NOT EXISTS test_schema")
        db.run("CREATE TABLE IF NOT EXISTS test_schema.test_table (i integer)")
        ds = Dataset(
            database_id=db.id,
            schema="test_schema",
            table_name="test_table",
            description="My Test Table",
        )
        superset_api.datasets.add(ds)
        c = Chart(
            datasource_id=ds.id,
            datasource_type="table",
            slice_name="My Test Chart",
            viz_type="table",
        )
        try:
            superset_api.charts.add(c)
        except Exception as e:
            print(e.__dict__)
            raise
        assert isinstance(c.id, int)
        assert superset_api.charts.get(id=c.id).slice_name == "My Test Chart"
        assert superset_api.charts.get(id=c.id).viz_type == "table"

        # Conflicting charts can apparently not be created

        # Test updating the item
        c.slice_name = "XXX"
        c.save()
        assert superset_api.charts.get(id=c.id).slice_name == "XXX"

        # Test deleting the item
        c.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            c.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

    def test_dashboards(self, superset_api):
        # Clean up any leftover items
        for i in superset_api.dashboards.find():
            i.delete()

        # Test getting an invalid item ID
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.dashboards.get(id=1)
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"

        # Test creating a new item
        d = Dashboard(
            dashboard_title="My Dashboard",
            published=True,
            slug="my_dashboard",
        )
        try:
            superset_api.dashboards.add(d)
        except Exception as e:
            print(e.__dict__)
            raise
        assert isinstance(d.id, int)
        assert superset_api.dashboards.get(id=d.id).dashboard_title == "My Dashboard"

        # Test creating a conflicting item
        d_id, d.id = d.id, None
        with pytest.raises(BadRequestError) as exc_info:
            superset_api.dashboards.add(d)
        d.id = d_id
        assert exc_info.value.response.status_code == 422
        assert exc_info.value.message == {'slug': ['Must be unique']}

        # Test updating the item
        d.dashboard_title = "XXX"
        d.save()
        assert superset_api.dashboards.get(id=d.id).dashboard_title == "XXX"

        # Test deleting the item
        d.delete()

        # Test deleting a non-existent item
        with pytest.raises(BadRequestError) as exc_info:
            d.delete()
        assert exc_info.value.response.status_code == 404
        assert exc_info.value.message == "Not found"
