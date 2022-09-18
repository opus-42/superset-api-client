def test_client(client):
    "Test basic superset client"

    assert client._token is not None
    assert client._token == {
        "access_token": "example_access_token",
        "refresh_token": "example_refresh_token",
    }
