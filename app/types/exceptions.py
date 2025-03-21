class APIException(Exception):
    """This is the base class for all API errors"""
    pass


class InvalidTokenError(APIException):
    """User has provided an invalid or expired token"""
    pass

class ExpiredSignatureError(APIException):
    """Token has expired and needs re-authentication."""
    pass
