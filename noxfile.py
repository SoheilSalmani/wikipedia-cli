import contextlib
import tempfile
from typing import Iterator

import nox
from nox.sessions import Session

package = "wikipedia_cli"
locations = "src", "tests", "noxfile.py"
nox.options.sessions = "lint", "mypy", "pytype", "safety", "tests"


class Poetry:
    def __init__(self, session: Session) -> None:
        self.session = session

    @contextlib.contextmanager
    def export(self, *args: str) -> Iterator[str]:
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
        output = self.session.run("poetry", "version", external=True, silent=True)
        return output.split()[1]

    def build(self, *args: str) -> None:
        self.session.run("poetry", "build", *args, external=True, silent=True)


def install_package(session: Session) -> None:
    poetry = Poetry(session)

    with poetry.export() as requirements:
        session.install(f"--requirement={requirements}")

    poetry.build("--format=wheel")

    version = poetry.version()
    session.install(
        "--no-deps", "--force-reinstall", f"dist/{package}-{version}-py3-none-any.whl"
    )


def install(session: Session, *args: str) -> None:
    poetry = Poetry(session)
    with poetry.export("--dev") as requirements:
        session.install(f"--constraint={requirements}", *args)


@nox.session(python=["3.9", "3.8"])
def lint(session: Session) -> None:
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
    args = session.posargs or locations
    install_package(session)
    install(session, "mypy")
    session.run("mypy", *args)


@nox.session(python=["3.9", "3.8"])
def pytype(session: Session) -> None:
    args = session.posargs or ["--disable=import-error", *locations]
    install_package(session)
    install(session, "pytype")
    session.run("pytype", *args)


@nox.session(python=["3.9"])
def safety(session: Session) -> None:
    poetry = Poetry(session)
    with poetry.export("--dev") as requirements:
        install(session, "safety")
        session.run("safety", "check", f"--file={requirements}", "--bare")


@nox.session(python=["3.9", "3.8"])
def tests(session: Session) -> None:
    args = session.posargs or ["--cov", "-m", "not e2e"]
    install_package(session)
    install(session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock")
    session.run("pytest", *args)


@nox.session(python=["3.9"])
def black(session: Session) -> None:
    args = session.posargs or locations
    install(session, "black")
    session.run("black", *args)


@nox.session(python=["3.9", "3.8"])
def typeguard(session: Session) -> None:
    args = session.posargs or ["-m", "not e2e"]
    install_package(session)
    install(session, "pytest", "pytest-mock", "typeguard")
    session.run("pytest", f"--typeguard-packages={package}", *args)
