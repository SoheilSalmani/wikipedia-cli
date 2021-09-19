from unittest.mock import Mock

import pytest
from pytest_mock import MockFixture

from wikipedia_cli import wikipedia


@pytest.fixture
def mock_requests_get(mocker: MockFixture) -> Mock:
    mock = mocker.patch("requests.get")
    mock.return_value.__enter__.return_value.json.return_value = {
        "title": "Title of the article",
        "extract": "Extract of the article.",
    }
    return mock


def test_get_random_uses_en_wikipedia_domain_by_default(
    mock_requests_get: Mock,
) -> None:
    wikipedia.get_random()
    args, _ = mock_requests_get.call_args
    assert "en.wikipedia.org" in args[0]


def test_get_random_uses_specified_wikipedia_domain(mock_requests_get: Mock) -> None:
    wikipedia.get_random(lang="de")
    args, _ = mock_requests_get.call_args
    assert "de.wikipedia.org" in args[0]


def test_random_page_returns_page(mock_requests_get: Mock) -> None:
    page = wikipedia.get_random()
    assert isinstance(page, wikipedia.Page)
