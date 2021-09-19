from _pytest.config import Config


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "unit: mark as unit test.")
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
