import nox
from nox import Session


@nox.session(python=["3.11", "3.12", "3.13"], reuse_venv=True)
@nox.parametrize("pydantic", ["1.10.27", "2.14.2"])
def tests(session: Session, pydantic):
    session.install("-e", ".", "pytest", "pytest-mock", f"pydantic=={pydantic}")
    session.run("pytest", "-q")
