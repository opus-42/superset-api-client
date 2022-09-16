from supersetapiclient.client import SupersetClient

client = SupersetClient(
    host="http://localhost:8080",
    username="admin",
    password="admin",
)

dashboards = client.dashboards.find()
dashboard = dashboards[0]

# Change color and title
print(dashboard.colors)
dashboard.update_colors({"label": "#fcba03"})
print(dashboard.colors)
dashboard.dashboard_title = "New title"

# Save all changes
dashboard.save()

# Fetch again
dashboards = client.dashboards.find()
print(dashboards)
