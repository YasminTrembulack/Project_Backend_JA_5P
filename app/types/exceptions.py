class APIException(Exception):
    """This is the base class for all API errors"""
    pass


class InvalidTokenError(APIException):
    """User has provided an invalid or expired token"""
    def __init__(self):
        super().__init__("Invalid token, please re-authenticate again.")


class ExpiredSignatureError(APIException):
    """Token has expired and needs re-authentication."""
    def __init__(self):
        super().__init__("Token has expired. Please log in again.")
