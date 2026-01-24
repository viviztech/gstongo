"""
Celery tasks for GSTONGO background jobs.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def filing_reminder(self, reminder_type=1):
    """
    Send filing reminders to customers.
    reminder_type: 1 = Early (1st-5th), 2 = GSTR-1 status (10th), 3 = GSTR-3B status (20th)
    """
    from apps.users.models import User
    from apps.gst_filing.models import GSTFiling
    from apps.notifications.models import Notification, NotificationTemplate
    
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year
    
    # Get users with pending filings for current month
    pending_filings = GSTFiling.objects.filter(
        status='pending',
        month=current_month,
        year=current_year
    ).select_related('user')
    
    users_with_pending = set(filing.user for filing in pending_filings)
    
    for user in users_with_pending:
        # Get user's pending filings
        user_filings = pending_filings.filter(user=user)
        filing_types = ', '.join(f.filing_type for f in user_filings)
        
        # Create notification
        Notification.objects.create(
            user=user,
            channel='push',
            category='filing_reminder',
            title='GST Filing Reminder',
            message=f'Please submit your {filing_types} filings for {today.strftime("%B %Y")}. Due date approaching.',
            reference_type='filing',
            reference_id=user_filings.first().id
        )
        
        # Send email notification
        try:
            send_mail(
                'GST Filing Reminder - GSTONGO',
                f'Dear {user.first_name},\n\nPlease submit your {filing_types} filings for {today.strftime("%B %Y")}.\n\nBest regards,\nGSTONGO Team',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f'Failed to send email to {user.email}: {e}')
    
    logger.info(f'Filing reminders sent to {len(users_with_pending)} users')
    return f'Reminders sent to {len(users_with_pending)} users'


@shared_task(bind=True)
def filing_status_check(self, filing_type):
    """
    Check filing status and notify users about status changes.
    filing_type: 'GSTR1' or 'GSTR3B'
    """
    from apps.gst_filing.models import GSTFiling
    from apps.notifications.models import Notification
    
    today = timezone.now().date()
    
    # Get filings that need status update (filed on or before today)
    filings = GSTFiling.objects.filter(
        filing_type=filing_type,
        status='pending',
        month=today.month,
        year=today.year
    ).select_related('user')
    
    for filing in filings:
        Notification.objects.create(
            user=filing.user,
            channel='push',
            category='filing_status',
            title=f'{filing_type} Filing Status',
            message=f'Your {filing_type} filing for {today.strftime("%B %Y")} is now due for submission.',
            reference_type='filing',
            reference_id=filing.id
        )
    
    logger.info(f'Filing status check completed for {filings.count()} {filing_type} filings')
    return f'Status check completed for {filings.count()} filings'


@shared_task(bind=True)
def payment_reminder(self):
    """
    Send payment reminders for pending invoices.
    """
    from apps.invoices.models import Invoice
    from apps.notifications.models import Notification
    from django.core.mail import send_mail
    
    today = timezone.now().date()
    
    # Get pending invoices
    pending_invoices = Invoice.objects.filter(
        status='issued'
    ).select_related('user')
    
    for invoice in pending_invoices:
        days_until_due = (invoice.due_date - today).days
        
        # Send reminder based on due date proximity
        if days_until_due <= 3:
            message = f'Payment due in {days_until_due} days. Invoice #{invoice.invoice_number} - ₹{invoice.total_amount}'
        elif days_until_due <= 7:
            message = f'Payment reminder: Invoice #{invoice.invoice_number} due in {days_until_due} days. Amount: ₹{invoice.total_amount}'
        else:
            message = f'Payment reminder: Invoice #{invoice.invoice_number} - ₹{invoice.total_amount} due on {invoice.due_date}'
        
        # Create notification
        Notification.objects.create(
            user=invoice.user,
            channel='push',
            category='payment_reminder',
            title='Payment Reminder',
            message=message,
            reference_type='invoice',
            reference_id=invoice.id
        )
        
        # Send email
        try:
            send_mail(
                f'Payment Reminder - Invoice #{invoice.invoice_number}',
                f'Dear {invoice.user.first_name},\n\n{message}\n\nBest regards,\nGSTONGO Team',
                settings.DEFAULT_FROM_EMAIL,
                [invoice.user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f'Failed to send payment reminder to {invoice.user.email}: {e}')
    
    logger.info(f'Payment reminders sent for {pending_invoices.count()} invoices')
    return f'Payment reminders sent for {pending_invoices.count()} invoices'


@shared_task(bind=True)
def generate_proforma_invoices(self):
    """
    Generate proforma invoices for completed filings.
    """
    from apps.invoices.models import ProformaInvoice, RateSlab
    from apps.gst_filing.models import GSTFiling
    from apps.notifications.models import Notification
    from django.db.models import Count
    from decimal import Decimal
    
    today = timezone.now().date()
    
    # Get filings that are declared but don't have proforma
    declared_filings = GSTFiling.objects.filter(
        status='pending',
        declaration_signed=True,
        declaration_signed_at__date=today
    ).exclude(
        id__in=ProformaInvoice.objects.values_list('related_filing_id', flat=True)
    )
    
    for filing in declared_filings:
        # Count invoices for this filing
        invoice_count = filing.invoices.count()
        
        # Get applicable rate slab
        slab = RateSlab.objects.filter(
            is_active=True,
            min_invoices__lte=invoice_count,
            max_invoices__gte=invoice_count,
            effective_from__lte=today
        ).first()
        
        if not slab:
            slab = RateSlab.objects.filter(
                is_active=True,
                min_invoices=0,
                max_invoices=0
            ).first()
        
        if slab:
            amount = slab.price
            gst_rate = Decimal('18.00')
            gst_amount = amount * gst_rate / 100
            total_amount = amount + gst_amount
            
            # Create proforma invoice
            proforma = ProformaInvoice.objects.create(
                user=filing.user,
                amount=amount,
                total_amount=total_amount,
                gst_rate=gst_rate,
                service_type=f'{filing.filing_type} Filing',
                description=f'{filing.filing_type} Filing Service for {filing.month}/{filing.year}',
                related_filing_id=filing.id
            )
            
            # Notify user
            Notification.objects.create(
                user=filing.user,
                channel='push',
                category='invoice_generated',
                title='Proforma Invoice Generated',
                message=f'Your proforma invoice #{proforma.invoice_number} for {filing.filing_type} filing is ready. Amount: ₹{total_amount}',
                reference_type='proforma_invoice',
                reference_id=proforma.id
            )
    
    logger.info(f'Generated {declared_filings.count()} proforma invoices')
    return f'Generated proforma invoices for {declared_filings.count()} filings'


@shared_task(bind=True)
def update_overdue_invoices(self):
    """
    Mark invoices as overdue if due date has passed.
    """
    from apps.invoices.models import Invoice
    from apps.notifications.models import Notification
    
    today = timezone.now().date()
    
    # Update invoices that are past due date
    updated_count = Invoice.objects.filter(
        status='issued',
        due_date__lt=today
    ).update(status='overdue')
    
    # Get overdue invoices for notification
    overdue_invoices = Invoice.objects.filter(
        status='overdue',
        due_date=today - timedelta(days=1)  # Newly overdue today
    ).select_related('user')
    
    for invoice in overdue_invoices:
        Notification.objects.create(
            user=invoice.user,
            channel='push',
            category='payment_reminder',
            title='Payment Overdue',
            message=f'Your invoice #{invoice.invoice_number} is now overdue. Amount: ₹{invoice.total_amount}. Please pay immediately to avoid service disruption.',
            reference_type='invoice',
            reference_id=invoice.id
        )
    
    logger.info(f'Marked {updated_count} invoices as overdue')
    return f'{updated_count} invoices marked as overdue'


@shared_task(bind=True)
def generate_monthly_report(self):
    """
    Generate and store monthly statistics.
    """
    from apps.admin_portal.models import AdminDashboardStats
    from apps.users.models import User
    from apps.gst_filing.models import GSTFiling
    from apps.invoices.models import Invoice, PaymentRecord
    from django.db.models import Sum
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Calculate statistics
    new_users = User.objects.filter(date_joined__date__gte=month_start).count()
    total_users = User.objects.filter(is_active=True).count()
    
    gstr1_filed = GSTFiling.objects.filter(
        filing_type='GSTR1',
        status='filed',
        filed_at__date__gte=month_start
    ).count()
    
    gstr3b_filed = GSTFiling.objects.filter(
        filing_type='GSTR3B',
        status='filed',
        filed_at__date__gte=month_start
    ).count()
    
    gstr9b_filed = GSTFiling.objects.filter(
        filing_type='GSTR9B',
        status='filed',
        filed_at__date__gte=month_start
    ).count()
    
    nil_filings = GSTFiling.objects.filter(
        nil_filing=True,
        declaration_signed_at__date__gte=month_start
    ).count()
    
    payments_collected = PaymentRecord.objects.filter(
        status='success',
        created_at__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_invoices = Invoice.objects.filter(status='issued').count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    overdue_amount = Invoice.objects.filter(
        status='overdue'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Store statistics
    stats = AdminDashboardStats.objects.create(
        date=month_start,
        new_users=new_users,
        total_users=total_users,
        gstr1_filed=gstr1_filed,
        gstr3b_filed=gstr3b_filed,
        gstr9b_filed=gstr9b_filed,
        nil_filings=nil_filings,
        payments_collected=payments_collected,
        pending_invoices=pending_invoices,
        overdue_invoices=overdue_invoices,
        overdue_amount=overdue_amount
    )
    
    logger.info(f'Monthly report generated for {month_start}')
    return f'Monthly report generated: {new_users} new users, ₹{payments_collected} collected'


@shared_task(bind=True)
def cleanup_expired_proforma_invoices(self):
    """
    Cancel proforma invoices that have expired.
    """
    from apps.invoices.models import ProformaInvoice
    
    today = timezone.now()
    
    # Update expired proforma invoices
    updated_count = ProformaInvoice.objects.filter(
        status='pending',
        valid_until__lt=today
    ).update(status='cancelled')
    
    logger.info(f'Cancelled {updated_count} expired proforma invoices')
    return f'{updated_count} expired proforma invoices cancelled'


@shared_task(bind=True)
def send_service_disablement_notifications(self):
    """
    Notify users about service disablement due to pending payments.
    """
    from apps.invoices.models import Invoice
    from apps.notifications.models import Notification
    from django.db.models import Max
    
    today = timezone.now().date()
    
    # Get users with pending invoices
    users_with_pending = Invoice.objects.filter(
        status__in=['issued', 'overdue']
    ).values('user').annotate(
        max_due_date=Max('due_date')
    )
    
    for user_data in users_with_pending:
        if user_data['max_due_date'] and (user_data['max_due_date'] - today).days <= -7:
            # User has invoice overdue by more than 7 days
            user_id = user_data['user']
            
            # Get user's latest invoice
            invoice = Invoice.objects.filter(
                user_id=user_id,
                status='overdue'
            ).order_by('-due_date').first()
            
            if invoice:
                Notification.objects.create(
                    user_id=user_id,
                    channel='push',
                    category='payment_reminder',
                    title='Service May Be Affected',
                    message=f'Your account has pending payments overdue by more than 7 days. Please clear dues immediately to avoid service disruption.',
                    reference_type='invoice',
                    reference_id=invoice.id
                )
    
    logger.info('Service disablement notifications sent')
    return 'Notifications sent for accounts with overdue payments'
