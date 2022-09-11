def test_connection(superset_api):
    assert superset_api.databases.find() == []
