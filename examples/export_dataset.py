from supersetapiclient.client import SupersetClient

client = SupersetClient(
    host="http://localhost:8080",
    username="admin",
    password="admin",
)

dataset = client.datasets.find(table_name="Example")[0]
client.datasets.export(id=dataset.id, name=dataset.table_name)
