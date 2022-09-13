#!/bin/bash

superset db upgrade
superset init
superset fab create-admin --username admin --firstname admin --lastname admin --email admin --password admin
if [ "${LOAD_EXAMPLES}" -eq "1" ]; then
  superset load_examples
fi
FLASK_ENV=development superset run -h 0.0.0.0 -p 8080
