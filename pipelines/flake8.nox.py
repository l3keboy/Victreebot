# IMPORTS
import nox

from pipelines import config


@nox.session(reuse_venv=True)
def flake8(session: nox.Session) -> None:
    """RUN code linting, SAST and analysis."""
    session.install("-r", "requirements.txt")
    session.run("flake8", *config.PYTHON_PATHS)
