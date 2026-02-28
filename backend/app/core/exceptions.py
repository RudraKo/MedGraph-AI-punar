from __future__ import annotations


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=400)


class DependencyUnavailableException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=503)
