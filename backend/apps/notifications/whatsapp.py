"""
WhatsApp Notification Service for GSTONGO
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    WhatsApp Business API integration for sending notifications.
    """
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v17.0"
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', None)
    
    def is_configured(self):
        """Check if WhatsApp is configured."""
        return bool(self.phone_number_id and self.access_token)
    
    def send_message(self, phone_number: str, message: str, template_name: str = None):
        """
        Send a WhatsApp message to a user.
        
        Args:
            phone_number: Recipient's phone number with country code
            message: Message text to send
            template_name: Optional template name for templated messages
            
        Returns:
            dict: Response with message ID or error
        """
        if not self.is_configured():
            logger.warning("WhatsApp is not configured")
            return {
                'success': False,
                'error': 'WhatsApp is not configured'
            }
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': phone_number,
                'type': 'text',
                'text': {'body': message},
            }
            
            if template_name:
                payload['type'] = 'template'
                payload['template'] = {
                    'name': template_name,
                    'language': {'code': 'en'},
                    'components': [
                        {
                            'type': 'body',
                            'parameters': [
                                {'type': 'text', 'text': message}
                            ]
                        }
                    ]
                }
            
            response = requests.post(
                f"{self.base_url}/{self.phone_number_id}/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'message_id': response_data.get('messages', [{}])[0].get('id'),
                    'phone_number': phone_number
                }
            else:
                logger.error(f"WhatsApp API error: {response_data}")
                return {
                    'success': False,
                    'error': response_data.get('error', {}).get('message', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"WhatsApp send error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_template_message(self, phone_number: str, template_name: str, parameters: dict):
        """
        Send a templated WhatsApp message.
        
        Args:
            phone_number: Recipient's phone number
            template_name: Name of the approved template
            parameters: Dictionary of template parameters
            
        Returns:
            dict: Response with message ID or error
        """
        if not self.is_configured():
            logger.warning("WhatsApp is not configured")
            return {
                'success': False,
                'error': 'WhatsApp is not configured'
            }
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
            }
            
            # Build template components
            components = []
            
            # Header component
            if 'header' in parameters:
                components.append({
                    'type': 'header',
                    'parameters': [
                        {'type': 'text', 'text': parameters['header']}
                    ]
                })
            
            # Body component
            if 'body' in parameters:
                body_params = []
                for param in parameters['body']:
                    body_params.append({'type': 'text', 'text': str(param)})
                components.append({
                    'type': 'body',
                    'parameters': body_params
                })
            
            # Button component (for OTP)
            if 'button_text' in parameters:
                components.append({
                    'type': 'button',
                    'sub_type': 'url',
                    'index': 0,
                    'parameters': [
                        {'type': 'text', 'text': parameters['button_text']}
                    ]
                })
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': phone_number,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {'code': parameters.get('language', 'en')},
                    'components': components
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{self.phone_number_id}/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'message_id': response_data.get('messages', [{}])[0].get('id'),
                    'phone_number': phone_number
                }
            else:
                logger.error(f"WhatsApp template error: {response_data}")
                return {
                    'success': False,
                    'error': response_data.get('error', {}).get('message', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"WhatsApp template send error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_otp(self, phone_number: str, otp: str):
        """
        Send OTP via WhatsApp.
        
        Args:
            phone_number: Recipient's phone number
            otp: One-time password
            
        Returns:
            dict: Response with message ID or error
        """
        return self.send_template_message(
            phone_number=phone_number,
            template_name='otp_verification',
            parameters={
                'header': otp,
                'body': [otp, '5 minutes'],
                'button_text': otp
            }
        )
    
    def send_filing_reminder(self, phone_number: str, filing_type: str, due_date: str):
        """
        Send GST filing reminder via WhatsApp.
        
        Args:
            phone_number: Recipient's phone number
            filing_type: Type of filing (GSTR-1, GSTR-3B, etc.)
            due_date: Due date for filing
            
        Returns:
            dict: Response with message ID or error
        """
        message = f"Reminder: Your {filing_type} filing is due on {due_date}. Please file your returns to avoid penalties."
        return self.send_message(phone_number, message)
    
    def send_payment_confirmation(self, phone_number: str, amount: str, invoice_number: str):
        """
        Send payment confirmation via WhatsApp.
        
        Args:
            phone_number: Recipient's phone number
            amount: Payment amount
            invoice_number: Invoice number
            
        Returns:
            dict: Response with message ID or error
        """
        message = f"Payment of ₹{amount} received for Invoice {invoice_number}. Thank you for your payment!"
        return self.send_message(phone_number, message)


# Singleton instance
whatsapp_service = WhatsAppService()
