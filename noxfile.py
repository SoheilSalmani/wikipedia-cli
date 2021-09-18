import contextlib
import tempfile

import nox

package = "wikipedia_cli"
locations = "src", "tests", "noxfile.py"


class Poetry:
    def __init__(self, session):
        self.session = session

    @contextlib.contextmanager
    def export(self, *args):
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

    def version(self):
        output = self.session.run("poetry", "version", external=True, silent=True)
        return output.split()[1]

    def build(self, *args):
        self.session.run("poetry", "build", *args, external=True, silent=True)


def install_package(session):
    poetry = Poetry(session)

    with poetry.export() as requirements:
        session.install(f"--requirement={requirements}")

    poetry.build("--format=wheel")

    version = poetry.version()
    session.install(
        "--no-deps", "--force-reinstall", f"dist/{package}-{version}-py3-none-any.whl"
    )


def install(session, *args):
    poetry = Poetry(session)
    with poetry.export("--dev") as requirements:
        session.install(f"--constraint={requirements}", *args)


@nox.session(python=["3.9", "3.8"])
def tests(session):
    args = session.posargs or ["--cov", "-m", "not e2e"]
    install_package(session)
    install(session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock")
    session.run("pytest", *args)


@nox.session(python=["3.9", "3.8"])
def lint(session):
    args = session.posargs or locations
    install(session, "flake8", "flake8-black", "flake8-import-order")
    session.run("flake8", *args)


@nox.session(python=["3.9"])
def black(session):
    args = session.posargs or locations
    install(session, "black")
    session.run("black", *args)
