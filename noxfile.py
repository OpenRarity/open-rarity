import nox
from nox import Session


@nox.session(python=["3.12", "3.13", "3.14", "3.15"], reuse_venv=True)
def tests(session: Session):
    session.install("-e", ".[opensea]", "pytest", "pytest-mock")
    session.run("pytest", "-q")
