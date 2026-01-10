"""
Management command to set up initial data for GSTONGO.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up initial data for GSTONGO application'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create rate slabs
        self.create_rate_slabs()
        
        # Create notification templates
        self.create_notification_templates()
        
        # Create default admin user (if not exists)
        self.create_default_admin()
        
        self.stdout.write(self.style.SUCCESS('Initial data setup complete!'))
    
    def create_rate_slabs(self):
        """Create default rate slabs for GST filing."""
        from apps.invoices.models import RateSlab
        
        rate_slabs = [
            {
                'name': 'Nil Filing',
                'min_invoices': 0,
                'max_invoices': 0,
                'price': Decimal('99.00'),
                'effective_from': timezone.now().date(),
            },
            {
                'name': 'Basic - 1 to 5 Invoices',
                'min_invoices': 1,
                'max_invoices': 5,
                'price': Decimal('150.00'),
                'effective_from': timezone.now().date(),
            },
            {
                'name': 'Standard - 6 to 10 Invoices',
                'min_invoices': 6,
                'max_invoices': 10,
                'price': Decimal('200.00'),
                'effective_from': timezone.now().date(),
            },
            {
                'name': 'Premium - 11 to 30 Invoices',
                'min_invoices': 11,
                'max_invoices': 30,
                'price': Decimal('300.00'),
                'effective_from': timezone.now().date(),
            },
        ]
        
        for slab_data in rate_slabs:
            slab, created = RateSlab.objects.update_or_create(
                min_invoices=slab_data['min_invoices'],
                max_invoices=slab_data['max_invoices'],
                defaults=slab_data
            )
            if created:
                self.stdout.write(f'  Created rate slab: {slab.name}')
            else:
                self.stdout.write(f'  Updated rate slab: {slab.name}')
    
    def create_notification_templates(self):
        """Create notification templates."""
        from apps.notifications.models import NotificationTemplate
        
        templates = [
            {
                'name': 'Registration OTP',
                'template_type': 'email',
                'category': 'otp',
                'subject': 'Your GSTONGO Verification Code',
                'body': 'Your verification code is: {{otp}}\n\nThis code will expire in 5 minutes.',
                'variables': ['otp'],
                'is_active': True,
            },
            {
                'name': 'Filing Reminder',
                'template_type': 'push',
                'category': 'filing_reminder',
                'subject': 'GST Filing Reminder',
                'body': 'Please submit your {{filing_type}} for {{month}} {{year}}. Due date approaching.',
                'variables': ['filing_type', 'month', 'year'],
                'is_active': True,
            },
            {
                'name': 'Filing Complete',
                'template_type': 'email',
                'category': 'filing_status',
                'subject': 'GST Filing Completed - {{filing_type}}',
                'body': 'Dear {{customer_name}},\n\nYour {{filing_type}} for {{month}} {{year}} has been successfully filed.\n\nReference Number: {{reference_number}}\nFiling Date: {{filing_date}}\n\nBest regards,\nGSTONGO Team',
                'variables': ['customer_name', 'filing_type', 'month', 'year', 'reference_number', 'filing_date'],
                'is_active': True,
            },
            {
                'name': 'Proforma Invoice',
                'template_type': 'email',
                'category': 'invoice_generated',
                'subject': 'Proforma Invoice Generated - {{invoice_number}}',
                'body': 'Dear {{customer_name}},\n\nYour proforma invoice is ready.\n\nInvoice Number: {{invoice_number}}\nAmount: ₹{{amount}}\nValid Until: {{valid_until}}\n\nPlease complete payment to proceed with your filing.\n\nBest regards,\nGSTONGO Team',
                'variables': ['customer_name', 'invoice_number', 'amount', 'valid_until'],
                'is_active': True,
            },
            {
                'name': 'Payment Reminder',
                'template_type': 'push',
                'category': 'payment_reminder',
                'subject': 'Payment Reminder',
                'body': 'Payment due for Invoice {{invoice_number}}. Amount: ₹{{amount}}. Due Date: {{due_date}}',
                'variables': ['invoice_number', 'amount', 'due_date'],
                'is_active': True,
            },
            {
                'name': 'Payment Received',
                'template_type': 'email',
                'category': 'payment_received',
                'subject': 'Payment Received - {{invoice_number}}',
                'body': 'Dear {{customer_name}},\n\nWe have received your payment of ₹{{amount}} for Invoice {{invoice_number}}.\n\nThank you for your payment.\n\nBest regards,\nGSTONGO Team',
                'variables': ['customer_name', 'invoice_number', 'amount'],
                'is_active': True,
            },
        ]
        
        for template_data in templates:
            template, created = NotificationTemplate.objects.update_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'  Created template: {template.name}')
            else:
                self.stdout.write(f'  Updated template: {template.name}')
    
    def create_default_admin(self):
        """Create default admin user."""
        from apps.users.models import User, AdminProfile
        from django.db import transaction
        
        admin_email = 'admin@gstongo.com'
        
        try:
            with transaction.atomic():
                # Create user if not exists
                user, created = User.objects.get_or_create(
                    email=admin_email,
                    defaults={
                        'first_name': 'Admin',
                        'last_name': 'User',
                        'is_staff': True,
                        'is_superuser': True,
                        'email_verified': True,
                    }
                )
                
                if created:
                    user.set_password('Admin@123')
                    user.save()
                    self.stdout.write(f'  Created admin user: {admin_email}')
                else:
                    self.stdout.write(f'  Admin user already exists: {admin_email}')
                
                # Create admin profile if not exists
                if not hasattr(user, 'admin_profile'):
                    AdminProfile.objects.create(
                        user=user,
                        employee_id='ADMIN001',
                        department='Administration',
                        designation='System Administrator',
                        can_manage_users=True,
                        can_manage_rate_slabs=True,
                        can_manage_filings=True,
                        can_manage_payments=True,
                        can_view_reports=True,
                        can_send_notifications=True,
                        can_manage_admins=True,
                    )
                    self.stdout.write('  Created admin profile')
                else:
                    self.stdout.write('  Admin profile already exists')
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  Warning: {str(e)}'))
