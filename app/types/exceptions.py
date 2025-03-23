class APIException(Exception):
    """This is the base class for all API errors"""
    def __init__(self, message: str = "Service is unavailable"):
        self.message = message
        super().__init__(message)


class InvalidTokenError(APIException):
    """User has provided an invalid or expired token"""
    def __init__(self):
        super().__init__("Invalid token, please re-authenticate again.")


class PermissionDeniedError(APIException):
    pass


class ExpiredSignatureError(APIException):
    """Token has expired and needs re-authentication."""
    pass


class AuthTokenMissingError(APIException):
    pass


class DatabaseConnectionError(APIException):
    pass


class MigrationExecutionError(APIException):
    pass


class NotAuthenticatedError(APIException):
    pass


class DataConflictError(APIException):
    pass


class InvalidCredentialsError(APIException):
    pass
