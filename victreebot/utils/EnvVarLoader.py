import os

from victreebot.exceptions.MissingEnvVariablesError import MissingEnvVariablesError


class EnvVarLoader:
    """Helper class to load variables from environment."""

    @classmethod
    def load_env_variable(cls, variable: str) -> str:
        """Load variable from environment."""
        value = os.getenv(variable)
        if value is None or value.isspace() or str(value).strip() == "":
            raise MissingEnvVariablesError(variable)

        return value

    @classmethod
    def load_optional_env_variable(cls, variable: str) -> str:
        """Load variable from environment."""
        value = os.getenv(variable)
        if value is None:
            return ""

        return value
