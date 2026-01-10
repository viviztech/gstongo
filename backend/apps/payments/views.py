"""
Payment Views for Razorpay Integration
"""
import json
import logging
from django.conf import settings
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

from .services import RazorpayService, PaymentError, verify_razorpay_webhook_signature
from .models import PaymentTransaction
from .serializers import PaymentInitSerializer, PaymentVerifySerializer, PaymentWebhookSerializer

logger = logging.getLogger(__name__)


class PaymentInitView(APIView):
    """
    Initialize a payment for an invoice or proforma.
    
    POST /api/v1/payments/init/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Initialize payment for invoice or proforma."""
        serializer = PaymentInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice_id = serializer.validated_data.get('invoice_id')
        proforma_id = serializer.validated_data.get('proforma_id')
        gateway = serializer.validated_data.get('gateway', 'razorpay')
        
        if gateway != 'razorpay':
            return Response(
                {'error': 'Only Razorpay is currently supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the invoice/proforma
            from apps.invoices.models import Invoice, ProformaInvoice
            
            invoice = None
            proforma = None
            amount = 0
            user = request.user
            
            if invoice_id:
                invoice = Invoice.objects.get(id=invoice_id, user=user)
                amount = invoice.total_amount
            elif proforma_id:
                proforma = ProformaInvoice.objects.get(id=proforma_id, user=user)
                amount = proforma.total_amount
            
            # Initialize Razorpay service
            razorpay_service = RazorpayService()
            
            # Create order
            order = razorpay_service.create_order(
                amount=amount,
                currency='INR',
                invoice_id=str(invoice.id if invoice else proforma.id),
                user_id=str(user.id),
                service_type=invoice.service_type if invoice else proforma.service_type,
                customer_email=user.email,
                customer_phone=user.phone_number,
                customer_name=f"{user.first_name} {user.last_name}",
            )
            
            # Create payment transaction record
            transaction = PaymentTransaction.objects.create(
                user=user,
                invoice=invoice,
                proforma=proforma,
                gateway='razorpay',
                gateway_order_id=order['order_id'],
                amount=amount,
                currency='INR',
                status='pending',
            )
            
            return Response({
                'order_id': order['order_id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key_id': order['key_id'],
                'transaction_id': transaction.id,
                'invoice_id': invoice_id,
                'proforma_id': proforma_id,
            })
            
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ProformaInvoice.DoesNotExist:
            return Response(
                {'error': 'Proforma invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PaymentError as e:
            return Response(
                {'error': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Payment initialization error: {str(e)}")
            return Response(
                {'error': 'Failed to initialize payment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentVerifyView(APIView):
    """
    Verify and confirm a payment.
    
    POST /api/v1/payments/verify/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Verify payment signature and update status."""
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
        razorpay_order_id = serializer.validated_data['razorpay_order_id']
        razorpay_signature = serializer.validated_data['razorpay_signature']
        
        transaction_id = serializer.validated_data.get('transaction_id')
        
        try:
            # Get transaction
            transaction = PaymentTransaction.objects.get(
                id=transaction_id,
                user=request.user,
                gateway_order_id=razorpay_order_id,
            )
            
            # Verify payment
            razorpay_service = RazorpayService()
            result = razorpay_service.verify_payment(
                payment_id=razorpay_payment_id,
                order_id=razorpay_order_id,
                signature=razorpay_signature,
            )
            
            if result['verified']:
                # Update transaction
                transaction.razorpay_payment_id = razorpay_payment_id
                transaction.razorpay_signature = razorpay_signature
                transaction.status = 'success'
                transaction.completed_at = timezone.now()
                transaction.save()
                
                # Update invoice/proforma status
                if transaction.invoice:
                    transaction.invoice.mark_as_paid(
                        method=result.get('method', 'online'),
                        reference=razorpay_payment_id
                    )
                if transaction.proforma:
                    transaction.proforma.status = 'paid'
                    transaction.proforma.save()
                
                # Send notification
                self.send_payment_success_notification(request.user, transaction)
                
                return Response({
                    'success': True,
                    'message': 'Payment verified successfully',
                    'transaction_id': transaction.id,
                    'payment_id': razorpay_payment_id,
                })
            else:
                # Mark transaction as failed
                transaction.status = 'failed'
                transaction.error_message = result.get('error', 'Verification failed')
                transaction.save()
                
                return Response({
                    'success': False,
                    'error': result.get('error', 'Payment verification failed'),
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except PaymentTransaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return Response(
                {'error': 'Failed to verify payment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def send_payment_success_notification(self, user, transaction):
        """Send payment success notification."""
        from apps.notifications.models import Notification
        from django.core.mail import send_mail
        
        # In-app notification
        Notification.objects.create(
            user=user,
            channel='push',
            category='payment_received',
            title='Payment Successful',
            message=f'Your payment of ₹{transaction.amount} has been received. Transaction ID: {transaction.razorpay_payment_id}',
            reference_type='transaction',
            reference_id=transaction.id
        )
        
        # Email notification
        try:
            send_mail(
                'Payment Received - GSTONGO',
                f'Dear {user.first_name},\n\nYour payment of ₹{transaction.amount} has been received successfully.\n\nTransaction Details:\n- Amount: ₹{transaction.amount}\n- Transaction ID: {transaction.razorpay_payment_id}\n- Date: {transaction.completed_at}\n\nThank you for your payment.\n\nBest regards,\nGSTONGO Team',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f'Failed to send payment email: {str(e)}')


class PaymentWebhookView(APIView):
    """
    Handle Razorpay webhooks.
    
    POST /api/v1/payments/webhook/
    """
    permission_classes = [permissions.AllowAny]  # Webhooks don't have auth
    
    def post(self, request):
        """Handle Razorpay webhook events."""
        # Get webhook signature from header
        webhook_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        
        # Verify webhook signature
        if webhook_secret:
            raw_body = request.body.decode('utf-8')
            if not verify_razorpay_webhook_signature(webhook_signature, webhook_secret, raw_body):
                logger.warning("Invalid webhook signature")
                return Response(
                    {'error': 'Invalid signature'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # Parse event
        event_data = json.loads(request.body)
        event_type = event_data.get('event')
        
        logger.info(f"Received Razorpay webhook: {event_type}")
        
        try:
            if event_type == 'payment.captured':
                self.handle_payment_captured(event_data.get('payload', {}))
            elif event_type == 'payment.failed':
                self.handle_payment_failed(event_data.get('payload', {}))
            elif event_type == 'refund.created':
                self.handle_refund_created(event_data.get('payload', {}))
            else:
                logger.info(f"Unhandled event type: {event_type}")
            
            return Response({'status': 'received'})
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return Response(
                {'error': 'Webhook processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def handle_payment_captured(self, payload):
        """Handle payment captured event."""
        payment = payload.get('payment', {})
        order_id = payment.get('order_id')
        payment_id = payment.get('id')
        
        transaction = PaymentTransaction.objects.filter(
            gateway_order_id=order_id
        ).first()
        
        if transaction:
            transaction.razorpay_payment_id = payment_id
            transaction.status = 'success'
            transaction.completed_at = timezone.now()
            transaction.save()
            
            # Update invoice/proforma
            if transaction.invoice:
                transaction.invoice.mark_as_paid('razorpay', payment_id)
            if transaction.proforma:
                transaction.proforma.status = 'paid'
                transaction.proforma.save()
    
    def handle_payment_failed(self, payload):
        """Handle payment failed event."""
        payment = payload.get('payment', {})
        order_id = payment.get('order_id')
        error_code = payment.get('error', {}).get('code')
        error_description = payment.get('error', {}).get('description')
        
        transaction = PaymentTransaction.objects.filter(
            gateway_order_id=order_id
        ).first()
        
        if transaction:
            transaction.status = 'failed'
            transaction.error_message = f"{error_code}: {error_description}"
            transaction.save()
    
    def handle_refund_created(self, payload):
        """Handle refund created event."""
        refund = payload.get('refund', {})
        payment_id = refund.get('payment_id')
        
        transaction = PaymentTransaction.objects.filter(
            razorpay_payment_id=payment_id
        ).first()
        
        if transaction:
            transaction.status = 'refunded'
            transaction.refund_id = refund.get('id')
            transaction.refund_amount = Decimal(refund.get('amount', 0)) / 100
            transaction.save()


@api_view(['GET'])
def payment_history(request):
    """
    Get payment history for current user.
    
    GET /api/v1/payments/history/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    transactions = PaymentTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    data = [
        {
            'id': t.id,
            'invoice_number': t.invoice.invoice_number if t.invoice else t.proforma.invoice_number if t.proforma else None,
            'amount': str(t.amount),
            'status': t.status,
            'gateway': t.gateway,
            'transaction_id': t.razorpay_payment_id,
            'created_at': t.created_at.isoformat(),
            'completed_at': t.completed_at.isoformat() if t.completed_at else None,
        }
        for t in transactions
    ]
    
    return Response(data)


@api_view(['GET'])
def payment_detail(request, transaction_id):
    """
    Get payment transaction details.
    
    GET /api/v1/payments/<transaction_id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    try:
        transaction = PaymentTransaction.objects.get(
            id=transaction_id,
            user=request.user
        )
        
        return Response({
            'id': transaction.id,
            'invoice_number': transaction.invoice.invoice_number if transaction.invoice else None,
            'amount': str(transaction.amount),
            'status': transaction.status,
            'gateway': transaction.gateway,
            'gateway_order_id': transaction.gateway_order_id,
            'gateway_payment_id': transaction.razorpay_payment_id,
            'error_message': transaction.error_message,
            'created_at': transaction.created_at.isoformat(),
            'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
        })
        
    except PaymentTransaction.DoesNotExist:
        return Response(
            {'error': 'Transaction not found'},
            status=status.HTTP_404_NOT_FOUND
        )
