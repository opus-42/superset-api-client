# superset-api-client
A Python Client for Apache Superset REST API

## Development
Install superset locally the following way:
1. Create .superset folder if not exists `mkdir .superset`
2. Initialize superset:
```bash
export SUPERSET_HOME=$(pwd)/.superset
superset db upgrade
superset init
superset fab create-admin
superset run
```