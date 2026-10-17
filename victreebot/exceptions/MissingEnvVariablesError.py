class MissingEnvVariablesError(Exception):
    """Exception raised when a required environment variable is missing."""

    def __init__(self, variable: str) -> None:
        self.message = f"The {variable} .env variable is missing or empty!"
        super().__init__(self.message)