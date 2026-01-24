"""
API Documentation schemas for Swagger/OpenAPI.
"""
from drf_yasg import openapi
from drf_yasg.openapi import Schema

# Authentication Schemas
login_request_schema = Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email address'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, format='password', description='User password'),
    },
    required=['email', 'password'],
)

login_response_schema = Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'user': Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        'tokens': Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                'access': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
    },
)

registration_request_schema = Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, min_length=8),
        'password_confirm': openapi.Schema(type=openapi.TYPE_STRING),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, min_length=2),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, min_length=2),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Optional phone number'),
    },
    required=['email', 'password', 'password_confirm', 'first_name', 'last_name'],
)

# GST Filing Schemas
filing_create_schema = Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'filing_type': openapi.Schema(
            type=openapi.TYPE_STRING,
            enum=['GSTR1', 'GSTR3B', 'GSTR9B'],
            description='Type of GST filing'
        ),
        'financial_year': openapi.Schema(type=openapi.TYPE_STRING, example='2024-25'),
        'month': openapi.Schema(type=openapi.TYPE_INTEGER, minimum=1, maximum=12),
        'year': openapi.Schema(type=openapi.TYPE_INTEGER, example=2024),
        'nil_filing': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
    },
    required=['filing_type', 'financial_year', 'month', 'year'],
)

filing_response_schema = Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
        'filing_type': openapi.Schema(type=openapi.TYPE_STRING),
        'financial_year': openapi.Schema(type=openapi.TYPE_STRING),
        'month': openapi.Schema(type=openapi.TYPE_INTEGER),
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['draft', 'pending', 'in_progress', 'filed', 'rejected']),
        'nil_filing': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'total_taxable_value': openapi.Schema(type=openapi.TYPE_NUMBER),
        'total_tax': openapi.Schema(type=openapi.TYPE_NUMBER),
        'declaration_statement': openapi.Schema(type=openapi.TYPE_STRING),
        'declaration_signed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'filing_reference_number': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
    },
)

# Invoice Schemas
invoice_response_schema = Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
        'invoice_number': openapi.Schema(type=openapi.TYPE_STRING),
        'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        'tax_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['issued', 'paid', 'overdue', 'cancelled']),
        'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
    },
)

# Error Response Schema
error_response_schema = Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
        'error': Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
    },
)

# Pagination Schema
paginated_response_schema = Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        'results': Schema(type=openapi.TYPE_ARRAY, items=Schema(type=openapi.TYPE_OBJECT)),
    },
)
