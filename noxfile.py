"""Nox sessions."""

import contextlib
import tempfile
from typing import Iterator

import nox
from nox.sessions import Session

wheel_prefix = "wikipedia_cli_by_ss"
package = "wikipedia_cli"
locations = "src", "tests", "noxfile.py", "docs/conf.py"
nox.options.sessions = "lint", "mypy", "pytype", "safety", "tests"


class Poetry:
    """Helper class for invoking Poetry inside a Nox session.

    Attributes:
        session: The Session object.
    """

    def __init__(self, session: Session) -> None:
        """Initialize self."""
        self.session = session

    @contextlib.contextmanager
    def export(self, *args: str) -> Iterator[str]:
        """Export the lock file to requirements format.

        Args:
            args: Command-line arguments for ``poetry export``.

        Yields:
            The path to the requirements file.
        """
        with tempfile.NamedTemporaryFile() as requirements:
            self.session.run(
                "poetry",
                "export",
                *args,
                "--format=requirements.txt",
                f"--output={requirements.name}",
                "--without-hashes",
                external=True,
            )
            yield requirements.name

    def version(self) -> str:
        """Retrieve the package version.

        Returns:
            The package version.
        """
        output = self.session.run("poetry", "version", external=True, silent=True)
        return output.split()[1]

    def build(self, *args: str) -> None:
        """Build the package.

        Args:
            args: Command-line arguments for ``poetry build``.
        """
        self.session.run("poetry", "build", *args, external=True, silent=True)


def install_package(session: Session) -> None:
    """Build and install the package.

    Build a wheel from the package, and install it into the virtual environment
    of the specified Nox session.

    The package requirements are installed using the versions specified in
    Poetry's lock file.

    Args:
        session: The Session object.
    """
    poetry = Poetry(session)

    with poetry.export() as requirements:
        session.install(f"--requirement={requirements}")

    poetry.build("--format=wheel")

    version = poetry.version()
    session.install(
        "--no-deps",
        "--force-reinstall",
        f"dist/{wheel_prefix}-{version}-py3-none-any.whl",
    )


def install(session: Session, *args: str) -> None:
    """Install development dependencies into the session's virtual environment.

    This function is a wrapper for nox.sessions.Session.install.

    The packages must be managed as development dependencies in Poetry.

    Args:
        session: The Session object.
        args: Command-line arguments for ``pip install``.
    """
    poetry = Poetry(session)
    with poetry.export("--dev") as requirements:
        session.install(f"--constraint={requirements}", *args)


@nox.session(python=["3.9", "3.8"])
def lint(session: Session) -> None:
    """Lint using Flake8."""
    args = session.posargs or locations
    install(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
    )
    session.run("flake8", *args)


@nox.session(python=["3.9", "3.8"])
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    install_package(session)
    install(session, "mypy")
    session.run("mypy", *args)


@nox.session(python=["3.9", "3.8"])
def pytype(session: Session) -> None:
    """Type-check using pytype."""
    args = session.posargs or ["--disable=import-error", *locations]
    install_package(session)
    install(session, "pytype")
    session.run("pytype", *args)


@nox.session(python=["3.9"])
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    poetry = Poetry(session)
    with poetry.export("--dev") as requirements:
        install(session, "safety")
        session.run("safety", "check", f"--file={requirements}", "--bare")


@nox.session(python=["3.9", "3.8"])
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov", "-m", "not e2e"]
    install_package(session)
    install(session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock")
    session.run("pytest", *args)


@nox.session(python=["3.9"])
def black(session: Session) -> None:
    """Run Black code formatter."""
    args = session.posargs or locations
    install(session, "black")
    session.run("black", *args)


@nox.session(python=["3.9", "3.8"])
def typeguard(session: Session) -> None:
    """Runtime type checking using Typeguard."""
    args = session.posargs or ["-m", "not e2e"]
    install_package(session)
    install(session, "pytest", "pytest-mock", "typeguard")
    session.run("pytest", f"--typeguard-packages={package}", *args)


@nox.session(python=["3.9", "3.8"])
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    install_package(session)
    install(session, "xdoctest")
    session.run("python", "-m", "xdoctest", package, *args)


@nox.session(python="3.9")
def docs(session: Session) -> None:
    """Build the documentation."""
    install_package(session)
    install(session, "sphinx", "sphinx-autodoc-typehints")
    session.run("sphinx-build", "docs", "docs/_build")


@nox.session(python="3.9")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    install(session, "coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
