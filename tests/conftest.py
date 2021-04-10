"""Fixture and superset app for testing."""
import pytest

from superset.app import create_app


app = create_app()

