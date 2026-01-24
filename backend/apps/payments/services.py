"""
Payment Gateway Service for Razorpay Integration
"""
import razorpay
from django.conf import settings
from decimal import Decimal
import logging
import hashlib
import hmac

logger = logging.getLogger(__name__)


class PaymentGatewayService:
    """Base payment gateway service."""
    
    def create_order(self, amount: Decimal, currency: str = 'INR', **kwargs):
        """Create a payment order."""
        raise NotImplementedError
    
    def verify_payment(self, payment_id: str, order_id: str, signature: str) -> bool:
        """Verify payment signature."""
        raise NotImplementedError
    
    def refund_payment(self, payment_id: str, amount: Decimal = None):
        """Initiate refund."""
        raise NotImplementedError
    
    def get_payment_status(self, payment_id: str):
        """Get payment status."""
        raise NotImplementedError


class RazorpayService(PaymentGatewayService):
    """Razorpay payment gateway integration."""
    
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
    
    def create_order(self, amount: Decimal, currency: str = 'INR', **kwargs) -> dict:
        """
        Create a Razorpay order for payment.
        
        Args:
            amount: Amount in INR (will be converted to paise)
            currency: Currency code (default: INR)
            **kwargs: Additional parameters like receipt, notes, customer info
        
        Returns:
            dict: Order details including order_id, amount, currency
        """
        try:
            # Convert amount to paise (Razorpay uses paise)
            amount_paise = int(amount * 100)
            
            order_data = {
                'amount': amount_paise,
                'currency': currency,
                'receipt': kwargs.get('receipt', f'receipt_{kwargs.get("invoice_id", "unknown")}'),
                'notes': {
                    'invoice_id': str(kwargs.get('invoice_id', '')),
                    'user_id': str(kwargs.get('user_id', '')),
                    'service_type': kwargs.get('service_type', 'GST Filing'),
                },
                'payment_capture': 1,  # Auto-capture payment
            }
            
            # Add customer details if provided
            if kwargs.get('customer_email'):
                order_data['customer_email'] = kwargs.get('customer_email')
            if kwargs.get('customer_phone'):
                order_data['customer_phone'] = kwargs.get('customer_phone')
            if kwargs.get('customer_name'):
                order_data['customer_name'] = kwargs.get('customer_name')
            
            order = self.client.order.create(data=order_data)
            
            logger.info(f"Razorpay order created: {order['id']} for amount ₹{amount}")
            
            return {
                'order_id': order['id'],
                'amount': amount,
                'amount_paise': amount_paise,
                'currency': currency,
                'key_id': self.key_id,
                'status': 'created',
            }
            
        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            raise PaymentError(f"Failed to create payment order: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating Razorpay order: {str(e)}")
            raise PaymentError("An error occurred while creating the payment order")
    
    def verify_payment(self, payment_id: str, order_id: str, signature: str) -> dict:
        """
        Verify Razorpay payment signature.
        
        Args:
            payment_id: Razorpay payment ID
            order_id: Razorpay order ID
            signature: Payment signature from client
        
        Returns:
            dict: Verification result with status
        """
        try:
            # Verify signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature,
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            
            logger.info(f"Payment verified successfully: {payment_id}")
            
            # Get payment details
            payment = self.client.payment.fetch(payment_id)
            
            return {
                'verified': True,
                'payment_id': payment_id,
                'order_id': order_id,
                'status': payment.get('status'),
                'amount': Decimal(payment.get('amount', 0)) / 100,
                'method': payment.get('method'),
                'email': payment.get('email'),
                'contact': payment.get('contact'),
            }
            
        except razorpay.errors.SignatureVerificationError as e:
            logger.error(f"Payment signature verification failed: {str(e)}")
            return {
                'verified': False,
                'error': 'Payment signature verification failed',
            }
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return {
                'verified': False,
                'error': str(e),
            }
    
    def refund_payment(self, payment_id: str, amount: Decimal = None) -> dict:
        """
        Initiate refund for a payment.
        
        Args:
            payment_id: Razorpay payment ID
            amount: Refund amount (optional, defaults to full payment)
        
        Returns:
            dict: Refund details
        """
        try:
            refund_data = {
                'payment_id': payment_id,
            }
            
            if amount:
                refund_data['amount'] = int(amount * 100)  # Convert to paise
                refund_data['speed'] = 'normal'
            
            refund = self.client.refund.create(data=refund_data)
            
            logger.info(f"Refund processed: {refund['id']} for payment {payment_id}")
            
            return {
                'refund_id': refund['id'],
                'payment_id': payment_id,
                'amount': Decimal(refund.get('amount', 0)) / 100,
                'status': refund.get('status'),
                'created_at': refund.get('created_at'),
            }
            
        except razorpay.errors.BadRequestError as e:
            logger.error(f"Refund failed: {str(e)}")
            raise PaymentError(f"Refund failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during refund: {str(e)}")
            raise PaymentError("An error occurred while processing the refund")
    
    def get_payment_status(self, payment_id: str) -> dict:
        """
        Get payment status from Razorpay.
        
        Args:
            payment_id: Razorpay payment ID
        
        Returns:
            dict: Payment details
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            
            return {
                'id': payment.get('id'),
                'order_id': payment.get('order_id'),
                'status': payment.get('status'),
                'amount': Decimal(payment.get('amount', 0)) / 100,
                'currency': payment.get('currency'),
                'method': payment.get('method'),
                'email': payment.get('email'),
                'contact': payment.get('contact'),
                'description': payment.get('description'),
                'bank': payment.get('bank'),
                'wallet': payment.get('wallet'),
                'vpa': payment.get('vpa'),
                'created_at': payment.get('created_at'),
            }
            
        except Exception as e:
            logger.error(f"Error fetching payment status: {str(e)}")
            raise PaymentError("Failed to fetch payment status")
    
    def create_customer(self, name: str, email: str, phone: str = None) -> dict:
        """
        Create a customer in Razorpay.
        
        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone number
        
        Returns:
            dict: Customer details
        """
        try:
            customer_data = {
                'name': name,
                'email': email,
            }
            
            if phone:
                customer_data['contact'] = phone
            
            customer = self.client.customer.create(data=customer_data)
            
            return {
                'customer_id': customer.get('id'),
                'name': customer.get('name'),
                'email': customer.get('email'),
                'contact': customer.get('contact'),
            }
            
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise PaymentError("Failed to create customer")
    
    def get_instrument_list(self, customer_id: str) -> list:
        """
        Get saved payment instruments for a customer.
        
        Args:
            customer_id: Razorpay customer ID
        
        Returns:
            list: Saved payment methods
        """
        try:
            instruments = self.client.instrument.all(
                customer_id=customer_id
            )
            
            return [
                {
                    'id': item.get('id'),
                    'type': item.get('type'),
                    'bank': item.get('bank'),
                    'last4': item.get('last4'),
                    'exp_month': item.get('exp_month'),
                    'exp_year': item.get('exp_year'),
                }
                for item in instruments.get('items', [])
            ]
            
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            return []


class PaymentError(Exception):
    """Custom exception for payment errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def generate_razorpay_signature(order_id: str, payment_id: str, razorpay_secret: str) -> str:
    """
    Generate HMAC signature for Razorpay webhook verification.
    
    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        razorpay_secret: Razorpay secret key
    
    Returns:
        str: HMAC signature
    """
    payload = f"{order_id}|{payment_id}"
    signature = hmac.new(
        razorpay_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_razorpay_webhook_signature(
    webhook_signature: str,
    webhook_secret: str,
    body: str
) -> bool:
    """
    Verify Razorpay webhook signature.
    
    Args:
        webhook_signature: Signature from webhook header
        webhook_secret: Webhook secret from Razorpay
        body: Raw request body
    
    Returns:
        bool: True if signature is valid
    """
    expected_signature = hmac.new(
        webhook_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(webhook_signature, expected_signature)
