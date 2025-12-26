"""Custom exceptions for EZ Runner."""


class EZRunnerError(Exception):
    """Base exception for EZ Runner."""

    pass


class ModelNotFoundError(EZRunnerError):
    """Model not found in any repository."""

    pass


class DockerError(EZRunnerError):
    """Docker-related error."""

    pass


class BuildError(EZRunnerError):
    """Image build error."""

    pass
