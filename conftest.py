import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-api",
        action="store_true",
        default=False,
        help="Run tests that make external API calls.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "api: test makes external API calls",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-api"):
        return

    skip_api = pytest.mark.skip(reason="API test; pass --run-api to run it")
    for item in items:
        if "api" in item.keywords:
            item.add_marker(skip_api)
