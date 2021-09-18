import pytest
import requests

from wikipedia_cli import console


@pytest.fixture
def mock_wikipedia_get_random(mocker):
    mock = mocker.patch("wikipedia_cli.wikipedia.get_random")
    mock.return_value = {
        "title": "Title of the article",
        "extract": "Extract of the article.",
    }
    return mock


@pytest.mark.unit
def test_main_returns_0(cli_runner, mock_wikipedia_get_random):
    result = cli_runner.invoke(console.main)
    assert result.exit_code == 0


@pytest.mark.unit
def test_main_prints_title(cli_runner, mock_wikipedia_get_random):
    result = cli_runner.invoke(console.main)
    assert "Title of the article" in result.output


@pytest.mark.unit
def test_main_uses_specified_lang(cli_runner, mock_wikipedia_get_random):
    cli_runner.invoke(console.main, ["--lang=pl"])
    mock_wikipedia_get_random.assert_called_with(lang="pl")


@pytest.mark.unit
def test_main_returns_1_on_request_exception(cli_runner, mock_wikipedia_get_random):
    mock_wikipedia_get_random.side_effect = requests.RequestException
    result = cli_runner.invoke(console.main)
    assert "Error" in result.output


@pytest.mark.e2e
def test_main_returns_0_in_production(cli_runner):
    result = cli_runner.invoke(console.main)
    assert result.exit_code == 0
