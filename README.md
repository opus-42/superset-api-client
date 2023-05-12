# superset-api-client
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://badge.fury.io/py/superset-api-client.svg)](https://badge.fury.io/py/superset-api-client)
[![Coverage Status](https://coveralls.io/repos/github/opus-42/superset-api-client/badge.svg?branch=develop)](https://coveralls.io/github/opus-42/superset-api-client?branch=develop)

A Python Client for Apache Superset REST API.

This is a Alpha version. Stability is not guaranteed.

## Usage

Setup a superset client:
```python3
from supersetapiclient.client import SupersetClient

client = SupersetClient(
    host="http://localhost:8080",
    username="admin",
    password="admin",
)
```

When developping in local (only), you may need to accept insecure transport (i.e. http).
This is NOT recommanded outside of local development environement, that is requesting `localhost`.

```python3
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
```

### Quickstart
Get all dashboards or find one by name:
```python3
# Get all dashboards
dashboards = client.dashboards.find()

# Get a dashboard by name
dashboard = client.dashboards.find(dashboard_title="Example")[0]
```

Update dashboard colors, some properties and save changes to server:
```python3
# Update label_colors mapping
print(dashboard.colors)
dashboard.update_colors({
    "label": "#fcba03"
})
print(dashboard.colors)

# Change dashboard title
dashboard.dashboard_title = "New title"

# Save all changes
dashboard.save()
```

### Export one ore more dashboard

You may export one or more dashboard user `client.dashboards` or directly on a `dashboard` object

```python3
# Export many dashboards
client.dashboards.export(
    # Set dashboard ids you would like to export
    [
        1,
        2
    ],
    "./dashboards.json" # A string or a path-like object where export will be saved
)

# Export one dashboard
dashboard.export(
    "./dashboard.json"
)
```

This functionality is also available in the same manner for datasets


# Contributing
Before committing to this repository, you must have [pre-commit](https://pre-commit.com) installed, and install
the following pre-commit hooks:

```sh
pre-commit install --install-hooks -t pre-commit -t pre-push
```

## Setting up a development envi

You will need Docker and docker-compose in order to run development environment.
To start development environment run:

```bash
    docker-compose up -d
```
