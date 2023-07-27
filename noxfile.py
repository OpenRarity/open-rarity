import nox
from nox import Session


@nox.session(python=["3.10", "3.11"], reuse_venv=True)
@nox.parametrize("pydantic", ["1.9.1", "2.0.3"])
def tests(session: Session, pydantic):
    session.install("poetry")
    session.run("poetry", "install")
    session.install(f"pydantic=={pydantic}")
    session.run("pytest")
