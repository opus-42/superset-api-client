from supersetapiclient.client import SupersetClient

client = SupersetClient(
    host="http://localhost:8080",
    username="admin",
    password="admin",
)

# Export one dashboard
dashboard = client.dashboards.find(dashboard_title="Unicode Test")[0]
dashboard.export("one_dashboard")


# Export multiple dashboards
client.dashboards.export(ids=[10, 11], path="./multiple_dashboards")
