"""Test cases for the wikipedia module."""

from unittest.mock import Mock

import marshmallow
import pytest
from pytest_mock import MockFixture

from wikipedia_cli import wikipedia


@pytest.fixture
def mock_requests_get(mocker: MockFixture) -> Mock:
    """Fixture for mocking requests.get."""
    mock = mocker.patch("requests.get")
    mock.return_value.__enter__.return_value.json.return_value = {
        "title": "Title of the article",
        "extract": "Extract of the article.",
    }
    return mock


@pytest.mark.unit
def test_get_random_uses_en_wikipedia_domain_by_default(
    mock_requests_get: Mock,
) -> None:
    """It uses the English Wikipedia language edition by default."""
    wikipedia.get_random()
    args, _ = mock_requests_get.call_args
    assert "en.wikipedia.org" in args[0]


@pytest.mark.unit
def test_get_random_uses_specified_wikipedia_domain(mock_requests_get: Mock) -> None:
    """It selects the specified Wikipedia language edition."""
    wikipedia.get_random(lang="de")
    args, _ = mock_requests_get.call_args
    assert "de.wikipedia.org" in args[0]


@pytest.mark.unit
def test_get_random_returns_page(mock_requests_get: Mock) -> None:
    """It returns an object of type Page."""
    page = wikipedia.get_random()
    assert isinstance(page, wikipedia.Page)


@pytest.mark.unit
def test_get_random_raises_validation_error_on_invalid_data(
    mock_requests_get: Mock,
) -> None:
    """It raises ValidationError when the fetched data is invalid."""
    mock_requests_get.return_value.__enter__.return_value.json.return_value = None
    with pytest.raises(marshmallow.ValidationError):
        wikipedia.get_random()
