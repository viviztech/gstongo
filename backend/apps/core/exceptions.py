"""
Custom exception handlers for GSTONGO.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class GSTONGOCustomException(Exception):
    """Base exception for GSTONGO."""
    
    def __init__(self, message, code=None, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.code = code or 'error'
        self.status_code = status_code
        super().__init__(message)


class ValidationError(GSTONGOCustomException):
    """Validation error exception."""
    
    def __init__(self, message, field=None):
        super().__init__(
            message=message,
            code='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST
        )
        self.field = field


class AuthenticationError(GSTONGOCustomException):
    """Authentication error exception."""
    
    def __init__(self, message='Authentication failed.'):
        super().__init__(
            message=message,
            code='authentication_error',
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class PermissionError(GSTONGOCustomException):
    """Permission error exception."""
    
    def __init__(self, message='You do not have permission to perform this action.'):
        super().__init__(
            message=message,
            code='permission_error',
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(GSTONGOCustomException):
    """Not found error exception."""
    
    def __init__(self, message='Resource not found.'):
        super().__init__(
            message=message,
            code='not_found',
            status_code=status.HTTP_404_NOT_FOUND
        )


class PaymentError(GSTONGOCustomException):
    """Payment related error exception."""
    
    def __init__(self, message='Payment processing failed.'):
        super().__init__(
            message=message,
            code='payment_error',
            status_code=status.HTTP_400_BAD_REQUEST
        )


class OTPAuthenticationError(GSTONGOCustomException):
    """OTP verification error."""
    
    def __init__(self, message='OTP verification failed.'):
        super().__init__(
            message=message,
            code='otp_error',
            status_code=status.HTTP_400_BAD_REQUEST
        )


def custom_exception_handler(exc, context):
    """Custom exception handler for DRF."""
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format
        response.data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            }
        }
        return response
    
    # Handle custom GSTONGO exceptions
    if isinstance(exc, GSTONGOCustomException):
        logger.error(f"GSTONGO Exception: {exc.message}")
        return Response(
            {
                'success': False,
                'error': {
                    'code': exc.code,
                    'message': exc.message,
                }
            },
            status=exc.status_code
        )
    
    # Log unexpected exceptions
    logger.exception(f"Unexpected error: {exc}")
    return Response(
        {
            'success': False,
            'error': {
                'code': 'internal_error',
                'message': 'An unexpected error occurred. Please try again later.',
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
