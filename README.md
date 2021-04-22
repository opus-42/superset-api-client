# superset-api-client
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

## Development

You will need Docker and docker-compose in order to run development environment.
To start development environnement run:

```bash
    docker-compose up -d
```
