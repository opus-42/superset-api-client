from pathlib import Path
import logging
from supersetapiclient.client import SupersetClient

client = SupersetClient(
    host="http://localhost:8080",
    username="admin",
    password="admin",
)

dashboard = client.dashboards.find(dashboard_title="Example")
client.dashboards.export_dashboard(id=dashboard.id, name=dashboard.dashboard_title)
