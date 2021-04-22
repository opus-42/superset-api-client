#!/bin/bash

superset db upgrade
superset init
superset fab create-admin --username admin --firstname admin --lastname admin --email admin --password admin
superset run -h 0.0.0.0 -p 8080