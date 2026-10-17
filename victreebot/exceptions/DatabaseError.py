class DatabaseError(Exception):
    """Exception raised when an interaction with the database failed."""

    def __init__(self) -> None:
        self.message = "Error interacting with the database."
        super().__init__(self.message)