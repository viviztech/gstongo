"""
Views for Invoices and Payments.
"""
import razorpay
from django.conf import settings
from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import RateSlab, ProformaInvoice, Invoice, PaymentRecord
from .serializers import (
    RateSlabSerializer, ProformaInvoiceSerializer, InvoiceSerializer,
    PaymentRecordSerializer, PaymentInitSerializer, PaymentWebhookSerializer
)


class RateSlabViewSet(viewsets.ModelViewSet):
    """ViewSet for Rate Slab management."""
    
    serializer_class = RateSlabSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile'):
            return RateSlab.objects.none()
        
        queryset = RateSlab.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('active')
        if is_active and is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('min_invoices')
    
    def create(self, request, *args, **kwargs):
        """Create new rate slab (admin only)."""
        if not hasattr(request.user, 'admin_profile') or not request.user.admin_profile.can_manage_rate_slabs:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update rate slab (admin only)."""
        if not hasattr(request.user, 'admin_profile') or not request.user.admin_profile.can_manage_rate_slabs:
            return Response(
                {'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class ProformaInvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Proforma Invoice operations."""
    
    serializer_class = ProformaInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ProformaInvoice.objects.filter(user=user)
        
        # Admins can see all
        if hasattr(user, 'admin_profile') and user.admin_profile.can_manage_payments:
            queryset = ProformaInvoice.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate proforma invoice for a filing."""
        filing_id = request.data.get('filing_id')
        invoice_count = request.data.get('invoice_count', 0)
        
        if not filing_id:
            return Response(
                {'error': 'filing_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get applicable rate slab
        today = timezone.now().date()
        slab = RateSlab.objects.filter(
            is_active=True,
            min_invoices__lte=invoice_count,
            max_invoices__gte=invoice_count,
            effective_from__lte=today
        ).first()
        
        if not slab:
            # Use default slab
            slab = RateSlab.objects.filter(
                is_active=True,
                min_invoices=0,
                max_invoices=0
            ).first()
        
        if not slab:
            return Response(
                {'error': 'No applicable rate slab found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate amounts
        amount = slab.price
        gst_rate = Decimal('18.00')
        gst_amount = amount * gst_rate / 100
        total_amount = amount + gst_amount
        
        # Create proforma invoice
        proforma = ProformaInvoice.objects.create(
            user=request.user,
            amount=amount,
            total_amount=total_amount,
            gst_rate=gst_rate,
            service_type='GST Filing',
            description=f'GST Filing Service - {invoice_count} invoices',
            related_filing_id=filing_id,
            valid_until=timezone.now() + timedelta(days=15)
        )
        
        return Response(
            ProformaInvoiceSerializer(proforma).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def convert_to_invoice(self, request, pk=None):
        """Convert proforma to final invoice."""
        proforma = self.get_object()
        
        if proforma.status != 'pending':
            return Response(
                {'error': 'Proforma is not pending.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if proforma.is_expired():
            return Response(
                {'error': 'Proforma has expired.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create final invoice
        invoice = Invoice.objects.create(
            proforma=proforma,
            user=proforma.user,
            amount=proforma.amount,
            total_amount=proforma.total_amount,
            gst_rate=proforma.gst_rate,
            service_type=proforma.service_type,
            description=proforma.description,
            due_date=timezone.now().date() + timedelta(days=30)
        )
        
        proforma.status = 'paid'
        proforma.save()
        
        return Response(InvoiceSerializer(invoice).data)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice operations."""
    
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.filter(user=user)
        
        # Admins can see all
        if hasattr(user, 'admin_profile') and user.admin_profile.can_manage_payments:
            queryset = Invoice.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List invoices with overdue flag."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Check for pending payments
        user_has_pending = Invoice.objects.filter(
            user=request.user,
            status__in=['issued', 'overdue']
        ).exists()
        
        return Response({
            'invoices': serializer.data,
            'has_pending_payments': user_has_pending,
            'pending_amount': sum(
                inv.total_amount for inv in
                Invoice.objects.filter(user=request.user, status__in=['issued', 'overdue'])
            )
        })


class PaymentViewSet(viewsets.ViewSet):
    """ViewSet for Payment operations."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """Initiate payment via payment gateway."""
        serializer = PaymentInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice_id = serializer.validated_data.get('invoice_id')
        proforma_id = serializer.validated_data.get('proforma_id')
        gateway = serializer.validated_data.get('gateway')
        
        # Get the document to pay for
        invoice = None
        proforma = None
        amount = 0
        user = request.user
        
        if invoice_id:
            try:
                invoice = Invoice.objects.get(id=invoice_id, user=user)
            except Invoice.DoesNotExist:
                return Response(
                    {'error': 'Invoice not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            amount = invoice.total_amount
        
        if proforma_id:
            try:
                proforma = ProformaInvoice.objects.get(id=proforma_id, user=user)
            except ProformaInvoice.DoesNotExist:
                return Response(
                    {'error': 'Proforma invoice not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            amount = proforma.total_amount
        
        # Initialize payment based on gateway
        if gateway == 'razorpay':
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            
            payment_data = {
                'amount': int(amount * 100),  # Convert to paise
                'currency': 'INR',
                'receipt': f'receipt_{uuid.uuid4().hex[:8]}',
                'notes': {
                    'user_id': str(user.id),
                    'invoice_id': str(invoice.id if invoice else proforma.id),
                }
            }
            
            razorpay_order = client.order.create(payment_data)
            
            # Create payment record
            payment = PaymentRecord.objects.create(
                user=user,
                invoice=invoice,
                proforma=proforma,
                amount=amount,
                gateway='razorpay',
                gateway_payment_id=razorpay_order['id'],
                status='pending'
            )
            
            return Response({
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'key_id': settings.RAZORPAY_KEY_ID,
                'payment_id': payment.id
            })
        
        return Response(
            {'error': 'Payment gateway not implemented.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """Handle payment gateway webhooks."""
        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        gateway = serializer.validated_data['gateway']
        event = serializer.validated_data['event']
        data = serializer.validated_data['data']
        
        # Handle different webhook events
        if gateway == 'razorpay':
            if event == 'payment.captured':
                order_id = data.get('order_id')
                payment = PaymentRecord.objects.get(gateway_payment_id=order_id)
                payment.status = 'success'
                payment.save()
                
                # Update invoice/proforma status
                if payment.invoice:
                    payment.invoice.mark_as_paid('razorpay', data.get('payment_id'))
                if payment.proforma:
                    payment.proforma.status = 'paid'
                    payment.proforma.save()
        
        return Response({'status': 'received'})
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get payment history for current user."""
        payments = PaymentRecord.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        return Response(
            PaymentRecordSerializer(payments, many=True).data
        )


class AdminPaymentViewSet(viewsets.ViewSet):
    """Admin viewset for payment management."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'admin_profile'):
            return PaymentRecord.objects.none()
        return PaymentRecord.objects.all()
    
    @action(detail=False, methods=['get'])
    def collection_summary(self, request):
        """Get payment collection summary."""
        if not hasattr(request.user, 'admin_profile'):
            return Response(
                {'error': 'Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.db.models import Sum
        
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # This month's collection
        month_collection = PaymentRecord.objects.filter(
            status='success',
            created_at__date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Overdue invoices
        overdue_invoices = Invoice.objects.filter(
            status='overdue'
        ).count()
        
        overdue_amount = Invoice.objects.filter(
            status='overdue'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        return Response({
            'this_month_collection': month_collection,
            'overdue_invoices_count': overdue_invoices,
            'overdue_amount': overdue_amount,
            'pending_invoices_count': Invoice.objects.filter(status='issued').count(),
        })
    
    @action(detail=True, methods=['post'])
    def record_manual_payment(self, request, pk=None):
        """Record manual payment."""
        if not hasattr(request.user, 'admin_profile'):
            return Response(
                {'error': 'Admin access required.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            invoice = Invoice.objects.get(id=pk)
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        amount = request.data.get('amount')
        method = request.data.get('method')
        reference = request.data.get('reference')
        
        if not all([amount, method, reference]):
            return Response(
                {'error': 'amount, method, and reference are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment record
        payment = PaymentRecord.objects.create(
            user=invoice.user,
            invoice=invoice,
            amount=amount,
            gateway='manual',
            gateway_payment_id=reference,
            status='success',
            payment_method=method
        )
        
        # Update invoice
        invoice.mark_as_paid(method, reference)
        
        return Response({
            'message': 'Payment recorded successfully.',
            'payment': PaymentRecordSerializer(payment).data
        })
