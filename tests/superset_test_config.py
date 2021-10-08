"""Configuration for tests"""
import tempfile

DEBUG = True
TESTING = True
WTF_CSRF_ENABLED = False

# APP CONFIG
# Creating a tempfile
SQLALCHEMY_DATABASE_URI = f"sqlite://{tempfile.mkdtemp()}/test.db"

# WEBSERVER
SUPERSET_WEBSERVER_ADDRESS = "0.0.0.0"
SUPERSET_WEBSERVER_PORT = 8080
