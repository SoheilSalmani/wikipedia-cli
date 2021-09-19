"""Test cases for the console module."""

from unittest.mock import Mock

from click.testing import CliRunner
import marshmallow
import pytest
from pytest_mock import MockFixture
import requests

from wikipedia_cli import console
from wikipedia_cli.wikipedia import page_schema


@pytest.fixture
def cli_runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.fixture
def mock_wikipedia_get_random(mocker: MockFixture) -> Mock:
    """Fixture for mocking wikipedia.get_random."""
    mock = mocker.patch("wikipedia_cli.wikipedia.get_random")
    mock.return_value = page_schema.load(
        {
            "title": "Title of the article",
            "extract": "Extract of the article.",
        }
    )
    return mock


@pytest.mark.unit
def test_main_returns_0(cli_runner: CliRunner, mock_wikipedia_get_random: Mock) -> None:
    """It exits with a status code of zero."""
    result = cli_runner.invoke(console.main)
    assert result.exit_code == 0


@pytest.mark.unit
def test_main_prints_title(
    cli_runner: CliRunner, mock_wikipedia_get_random: Mock
) -> None:
    """It prints the title of the Wikipedia page."""
    result = cli_runner.invoke(console.main)
    assert "Title of the article" in result.output


@pytest.mark.unit
def test_main_uses_specified_lang(
    cli_runner: CliRunner, mock_wikipedia_get_random: Mock
) -> None:
    """It uses the specified language edition of Wikipedia."""
    cli_runner.invoke(console.main, ["--lang=pl"])
    mock_wikipedia_get_random.assert_called_with(lang="pl")


@pytest.mark.unit
def test_main_handles_request_exceptions(
    cli_runner: CliRunner, mock_wikipedia_get_random: Mock
) -> None:
    """It exists with a non-zero status code if the request fails."""
    mock_wikipedia_get_random.side_effect = requests.RequestException("request failed")
    result = cli_runner.invoke(console.main)
    assert "Error" in result.output


@pytest.mark.unit
def test_main_handles_validation_errors(
    cli_runner: CliRunner, mock_wikipedia_get_random: Mock
) -> None:
    """It raises `ClickException` when validation fails."""
    mock_wikipedia_get_random.side_effect = marshmallow.ValidationError("invalid data")
    result = cli_runner.invoke(console.main)
    assert "Error" in result.output


@pytest.mark.e2e
def test_main_returns_0_in_production(cli_runner: CliRunner) -> None:
    """It exists with a status code of zero (end-to-end)."""
    result = cli_runner.invoke(console.main)
    assert result.exit_code == 0
