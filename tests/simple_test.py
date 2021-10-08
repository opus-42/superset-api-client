
def test_client(client):
    "Test basic superset client"

    assert client.token is not None