import click.testing
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "unit: mark as unit test.")
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
