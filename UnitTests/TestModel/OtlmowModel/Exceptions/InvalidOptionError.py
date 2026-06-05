class InvalidOptionError(ValueError):
    """
    Exception raised when an invalid option is provided.
    """

    def __init__(self, message: str, closest_matches: list[str] = None):
        super().__init__(message)
        self.message: str = message
        self.closest_matches: list[str] = closest_matches or []
