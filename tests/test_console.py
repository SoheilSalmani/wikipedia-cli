from unittest.mock import Mock

from click.testing import CliRunner
import pytest
from pytest_mock import MockFixture
import requests

from wikipedia_cli import console
from wikipedia_cli.wikipedia import page_schema


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_wikipedia_get_random(mocker: MockFixture) -> Mock:
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
    result = cli_runner.invoke(console.main)
    assert result.exit_code == 0


@pytest.mark.unit
def test_main_prints_title(
    cli_runner: CliRunner, mock_wikipedia_get_random: Mock
) -> None:
    result = cli_runner.invoke(console.main)
    assert "Title of the article" in result.output


@pytest.mark.unit
def test_main_uses_specified_lang(
    cli_runner: CliRunner, mock_wikipedia_get_random: Mock
) -> None:
    cli_runner.invoke(console.main, ["--lang=pl"])
    mock_wikipedia_get_random.assert_called_with(lang="pl")


@pytest.mark.unit
def test_main_returns_1_on_request_exception(
    cli_runner: CliRunner, mock_wikipedia_get_random: Mock
) -> None:
    mock_wikipedia_get_random.side_effect = requests.RequestException
    result = cli_runner.invoke(console.main)
    assert "Error" in result.output


@pytest.mark.e2e
def test_main_returns_0_in_production(cli_runner: CliRunner):
    result = cli_runner.invoke(console.main)
    assert result.exit_code == 0
