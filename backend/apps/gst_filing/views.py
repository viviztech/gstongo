"""
Views for GST Filing module.
"""
import pandas as pd
import uuid
import io
from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.utils import timezone

from .models import GSTFiling, GSTR1Details, GSTR3BDetails, GSTR9BDetails, Invoice, FilingDocument
from .serializers import (
    GSTFilingSerializer, GSTFilingCreateSerializer, GSTFilingUpdateSerializer,
    GSTR1DetailsSerializer, GSTR3BDetailsSerializer, GSTR9BDetailsSerializer,
    InvoiceSerializer, InvoiceUploadSerializer, DeclarationSerializer,
    FilingStatusSerializer, NilFilingSerializer, FilingSummarySerializer
)


class GSTFilingViewSet(viewsets.ModelViewSet):
    """ViewSet for GST Filing operations."""
    
    serializer_class = GSTFilingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter filings by user."""
        user = self.request.user
        queryset = GSTFiling.objects.filter(user=user)
        
        # Filter by filing type
        filing_type = self.request.query_params.get('filing_type', None)
        if filing_type:
            queryset = queryset.filter(filing_type=filing_type)
        
        # Filter by status
        filing_status = self.request.query_params.get('status', None)
        if filing_status:
            queryset = queryset.filter(status=filing_status)
        
        # Filter by financial year
        financial_year = self.request.query_params.get('financial_year', None)
        if financial_year:
            queryset = queryset.filter(financial_year=financial_year)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return GSTFilingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return GSTFilingUpdateSerializer
        return GSTFilingSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new GST filing."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filing = serializer.save()
        
        # Create corresponding details based on filing type
        if filing.filing_type == 'GSTR1':
            GSTR1Details.objects.create(filing=filing)
        elif filing.filing_type == 'GSTR3B':
            GSTR3BDetails.objects.create(filing=filing)
        elif filing.filing_type == 'GSTR9B':
            GSTR9BDetails.objects.create(filing=filing)
        
        return Response(
            GSTFilingSerializer(filing).data,
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Get filing details with all related data."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Include filing type specific details
        if instance.filing_type == 'GSTR1':
            data['details'] = GSTR1DetailsSerializer(instance.gstr1_details).data
        elif instance.filing_type == 'GSTR3B':
            data['details'] = GSTR3BDetailsSerializer(instance.gstr3b_details).data
        elif instance.filing_type == 'GSTR9B':
            data['details'] = GSTR9BDetailsSerializer(instance.gstr9b_details).data
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get filing summary."""
        filing = self.get_object()
        invoices = filing.invoices.all()
        
        summary = {
            'filing': GSTFilingSerializer(filing).data,
            'invoice_count': invoices.count(),
            'total_taxable_value': sum(inv.taxable_value for inv in invoices),
            'total_tax': sum(inv.total_tax for inv in invoices),
            'invoice_types': {},
        }
        
        # Group by invoice type
        for invoice_type, _ in Invoice.INVOICE_TYPE_CHOICES:
            type_invoices = invoices.filter(invoice_type=invoice_type)
            if type_invoices.exists():
                summary['invoice_types'][invoice_type] = {
                    'count': type_invoices.count(),
                    'value': sum(inv.taxable_value for inv in type_invoices),
                }
        
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def upload_invoices(self, request, pk=None):
        """Upload invoices via Excel file."""
        filing = self.get_object()
        
        if filing.filing_locked:
            return Response(
                {'error': 'Filing is locked. Cannot modify.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InvoiceUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = serializer.validated_data['file']
        
        try:
            # Read Excel file
            df = pd.read_excel(file)
            
            # Process and create invoices
            invoices_data = []
            for _, row in df.iterrows():
                invoice = Invoice(
                    filing=filing,
                    invoice_number=str(row.get('invoice_number', '')),
                    invoice_date=row.get('invoice_date'),
                    invoice_type=row.get('invoice_type', 'b2b'),
                    counterparty_gstin=row.get('counterparty_gstin'),
                    counterparty_name=row.get('counterparty_name'),
                    taxable_value=row.get('taxable_value', 0),
                    igst=row.get('igst', 0),
                    cgst=row.get('cgst', 0),
                    sgst=row.get('sgst', 0),
                    cess=row.get('cess', 0),
                    total_tax=row.get('total_tax', 0),
                    hsn_code=row.get('hsn_code'),
                )
                invoices_data.append(invoice)
            
            # Bulk create invoices
            Invoice.objects.bulk_create(invoices_data)
            
            # Update filing totals
            filing.calculate_totals()
            
            return Response({
                'message': f'{len(invoices_data)} invoices uploaded successfully.',
                'invoice_count': len(invoices_data)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error processing file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def declare(self, request, pk=None):
        """Submit filing declaration."""
        filing = self.get_object()
        
        if filing.filing_locked:
            return Response(
                {'error': 'Filing is locked.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DeclarationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filing.declaration_statement = serializer.validated_data['declaration_statement']
        filing.declaration_signed = True
        filing.declaration_signed_at = timezone.now()
        filing.status = 'pending'
        filing.save()
        
        return Response({
            'message': 'Declaration submitted successfully.',
            'filing': GSTFilingSerializer(filing).data
        })
    
    @action(detail=True, methods=['post'])
    def mark_nil(self, request, pk=None):
        """Mark filing as nil return."""
        filing = self.get_object()
        
        serializer = NilFilingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filing.nil_filing = True
        filing.declaration_statement = serializer.validated_data['declaration_statement']
        filing.declaration_signed = True
        filing.declaration_signed_at = timezone.now()
        filing.status = 'pending'
        filing.save()
        
        return Response({
            'message': 'Nil return marked successfully.',
            'filing': GSTFilingSerializer(filing).data
        })
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get filing template information."""
        filing_type = request.query_params.get('type')
        financial_year = request.query_params.get('financial_year')
        
        if not filing_type or not financial_year:
            return Response(
                {'error': 'Filing type and financial year are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Template configurations
        templates = {
            'GSTR1': {
                'columns': [
                    {'name': 'invoice_number', 'type': 'string', 'required': True, 'description': 'Invoice number'},
                    {'name': 'invoice_date', 'type': 'date', 'required': True, 'description': 'Invoice date (YYYY-MM-DD)'},
                    {'name': 'invoice_type', 'type': 'string', 'required': True, 'description': 'b2b, b2c, export, debit-note, credit-note'},
                    {'name': 'counterparty_gstin', 'type': 'string', 'required': False, 'description': 'Recipient GSTIN (15 chars for B2B)'},
                    {'name': 'counterparty_name', 'type': 'string', 'required': True, 'description': 'Recipient name'},
                    {'name': 'taxable_value', 'type': 'number', 'required': True, 'description': 'Taxable amount'},
                    {'name': 'igst', 'type': 'number', 'required': False, 'description': 'IGST amount'},
                    {'name': 'cgst', 'type': 'number', 'required': False, 'description': 'CGST amount'},
                    {'name': 'sgst', 'type': 'number', 'required': False, 'description': 'SGST/UTGST amount'},
                    {'name': 'cess', 'type': 'number', 'required': False, 'description': 'Cess amount'},
                    {'name': 'total_tax', 'type': 'number', 'required': True, 'description': 'Total tax amount'},
                    {'name': 'hsn_code', 'type': 'string', 'required': False, 'description': 'HSN/SAC code (8 digits)'},
                    {'name': 'export_port', 'type': 'string', 'required': False, 'description': 'Export port (for exports)'},
                    {'name': 'shipping_bill_number', 'type': 'string', 'required': False, 'description': 'Shipping bill number (for exports)'},
                    {'name': 'shipping_bill_date', 'type': 'date', 'required': False, 'description': 'Shipping bill date (for exports)'},
                ],
                'description': 'Template for GSTR-1 outward supplies data',
                'instructions': [
                    '1. Fill in all mandatory columns',
                    '2. For B2B invoices, counterparty_gstin must be 15 characters',
                    '3. For exports, fill export details columns',
                    '4. Tax amounts should match taxable_value * tax rate',
                    '5. Date format: YYYY-MM-DD'
                ]
            },
            'GSTR3B': {
                'columns': [
                    {'name': 'description', 'type': 'string', 'required': True, 'description': 'Tax category description'},
                    {'name': 'taxable_value', 'type': 'number', 'required': True, 'description': 'Taxable value'},
                    {'name': 'igst', 'type': 'number', 'required': False, 'description': 'IGST amount'},
                    {'name': 'cgst', 'type': 'number', 'required': False, 'description': 'CGST amount'},
                    {'name': 'sgst', 'type': 'number', 'required': False, 'description': 'SGST amount'},
                    {'name': 'cess', 'type': 'number', 'required': False, 'description': 'Cess amount'},
                ],
                'description': 'Template for GSTR-3B summary data',
                'instructions': [
                    '1. Enter summary data for outward supplies',
                    '2. Include ITC reversal amounts',
                    '3. Include interest and late fee if applicable'
                ]
            },
            'GSTR9B': {
                'columns': [
                    {'name': 'item_description', 'type': 'string', 'required': True, 'description': 'Item/category description'},
                    {'name': 'outward_supplies', 'type': 'number', 'required': True, 'description': 'Total outward supplies'},
                    {'name': 'inward_supplies', 'type': 'number', 'required': True, 'description': 'Total inward supplies'},
                    {'name': 'tax_collected', 'type': 'number', 'required': True, 'description': 'Total tax collected'},
                    {'name': 'tax_deposited', 'type': 'number', 'required': True, 'description': 'Total tax deposited'},
                    {'name': 'itc_claimed', 'type': 'number', 'required': True, 'description': 'ITC claimed'},
                    {'name': 'itc_reversed', 'type': 'number', 'required': True, 'description': 'ITC reversed'},
                ],
                'description': 'Template for GSTR-9B annual return data',
                'instructions': [
                    '1. Enter annual summary data',
                    '2. Include all ITC details',
                    '3. Ensure tax collected matches deposits'
                ]
            }
        }
        
        if filing_type not in templates:
            return Response(
                {'error': 'Invalid filing type. Use GSTR1, GSTR3B, or GSTR9B.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(templates[filing_type])
    
    @action(detail=False, methods=['get'])
    def download_template(self, request):
        """Download Excel template for filing."""
        filing_type = request.query_params.get('type')
        financial_year = request.query_params.get('financial_year')
        
        if not filing_type or not financial_year:
            return Response(
                {'error': 'Filing type and financial year are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Template column definitions
        templates = {
            'GSTR1': [
                'invoice_number', 'invoice_date', 'invoice_type',
                'counterparty_gstin', 'counterparty_name',
                'taxable_value', 'igst', 'cgst', 'sgst', 'cess',
                'total_tax', 'hsn_code', 'export_port',
                'shipping_bill_number', 'shipping_bill_date'
            ],
            'GSTR3B': [
                'description', 'taxable_value', 'igst', 'cgst', 'sgst', 'cess'
            ],
            'GSTR9B': [
                'item_description', 'outward_supplies', 'inward_supplies',
                'tax_collected', 'tax_deposited', 'itc_claimed', 'itc_reversed'
            ]
        }
        
        if filing_type not in templates:
            return Response(
                {'error': 'Invalid filing type. Use GSTR1, GSTR3B, or GSTR9B.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create DataFrame with template columns
        columns = templates[filing_type]
        df = pd.DataFrame(columns=columns)
        
        # Add sample data row for reference
        sample_data = {
            'GSTR1': {
                'invoice_number': 'INV-001',
                'invoice_date': '2024-04-01',
                'invoice_type': 'b2b',
                'counterparty_gstin': '27AAAAA0000A1Z5',
                'counterparty_name': 'Sample Company Pvt Ltd',
                'taxable_value': 10000.00,
                'igst': 1800.00,
                'cgst': 0.00,
                'sgst': 0.00,
                'cess': 0.00,
                'total_tax': 1800.00,
                'hsn_code': '85311000',
                'export_port': '',
                'shipping_bill_number': '',
                'shipping_bill_date': ''
            },
            'GSTR3B': {
                'description': 'Outward taxable supplies',
                'taxable_value': 50000.00,
                'igst': 9000.00,
                'cgst': 0.00,
                'sgst': 0.00,
                'cess': 0.00
            },
            'GSTR9B': {
                'item_description': 'Total Outward Supplies',
                'outward_supplies': 600000.00,
                'inward_supplies': 400000.00,
                'tax_collected': 108000.00,
                'tax_deposited': 108000.00,
                'itc_claimed': 72000.00,
                'itc_reversed': 5000.00
            }
        }
        
        # Add sample row (first row after header)
        df = pd.concat([df, pd.DataFrame([sample_data[filing_type]])], ignore_index=True)
        
        # Create Excel file in memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=filing_type)
            
            # Add instructions sheet
            instructions = pd.DataFrame({
                'Instruction': [
                    f'This is the {filing_type} template for financial year {financial_year}',
                    'Fill in your data starting from row 2 (row 1 is the header)',
                    'Do not change the column names or order',
                    'For dates, use format YYYY-MM-DD',
                    'For numbers, do not use thousand separators',
                    'Save as .xlsx format and upload',
                    '',
                    'Invoice Types:',
                    '  - b2b: Business to Business (requires 15-char GSTIN)',
                    '  - b2c: Business to Consumer',
                    '  - export: Export invoices',
                    '  - debit-note: Debit notes',
                    '  - credit-note: Credit notes'
                ]
            })
            instructions.to_excel(writer, index=False, sheet_name='Instructions')
        
        # Prepare response
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filing_type}_template_{financial_year}.xlsx'
        
        return response


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice operations."""
    
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter invoices by filing and user."""
        filing_id = self.request.query_params.get('filing_id')
        if filing_id:
            return Invoice.objects.filter(filing__user=self.request.user, filing_id=filing_id)
        return Invoice.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Create a new invoice."""
        filing_id = request.data.get('filing_id')
        try:
            filing = GSTFiling.objects.get(id=filing_id, user=request.user)
        except GSTFiling.DoesNotExist:
            return Response(
                {'error': 'Filing not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if filing.filing_locked:
            return Response(
                {'error': 'Filing is locked. Cannot add invoices.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save(filing=filing)
        
        # Update filing totals
        filing.calculate_totals()
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete an invoice."""
        try:
            invoice = self.get_object()
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        filing = invoice.filing
        if filing.filing_locked:
            return Response(
                {'error': 'Filing is locked. Cannot delete invoices.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.delete()
        
        # Update filing totals
        filing.calculate_totals()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class FilingAdminViewSet(viewsets.ModelViewSet):
    """ViewSet for admin filing operations."""
    
    serializer_class = GSTFilingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Admin can see all filings."""
        if not hasattr(self.request.user, 'admin_profile'):
            return GSTFiling.objects.none()
        
        queryset = GSTFiling.objects.all()
        
        # Apply filters
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        filing_type = self.request.query_params.get('filing_type')
        if filing_type:
            queryset = queryset.filter(filing_type=filing_type)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update filing status (admin only)."""
        filing = self.get_object()
        
        serializer = FilingStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filing.status = serializer.validated_data['status']
        if serializer.validated_data.get('filing_reference_number'):
            filing.filing_reference_number = serializer.validated_data['filing_reference_number']
        
        if filing.status == 'filed':
            filing.filed_at = timezone.now()
        
        filing.save()
        
        return Response(GSTFilingSerializer(filing).data)
    
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock filing for customer."""
        filing = self.get_object()
        reason = request.data.get('reason', 'Locked by admin')
        
        filing.filing_locked = True
        filing.lock_reason = reason
        filing.save()
        
        return Response({
            'message': 'Filing locked successfully.',
            'lock_reason': filing.lock_reason
        })
    
    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock filing for customer."""
        filing = self.get_object()
        
        filing.filing_locked = False
        filing.lock_reason = None
        filing.save()
        
        return Response({'message': 'Filing unlocked successfully.'})
    
    @action(detail=True, methods=['post'])
    def trigger_reminder(self, request, pk=None):
        """Send reminder to customer."""
        filing = self.get_object()
        
        # TODO: Integrate with notification system
        return Response({
            'message': f'Reminder sent to {filing.user.email}'
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics."""
        if not hasattr(request.user, 'admin_profile'):
            return Response(
                {'error': 'Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_filings': GSTFiling.objects.count(),
            'pending_filings': GSTFiling.objects.filter(status='pending').count(),
            'filed_filings': GSTFiling.objects.filter(status='filed').count(),
            'nil_filings': GSTFiling.objects.filter(nil_filing=True).count(),
            'by_type': {
                'GSTR1': GSTFiling.objects.filter(filing_type='GSTR1').count(),
                'GSTR3B': GSTFiling.objects.filter(filing_type='GSTR3B').count(),
                'GSTR9B': GSTFiling.objects.filter(filing_type='GSTR9B').count(),
            }
        }
        
        return Response(stats)
