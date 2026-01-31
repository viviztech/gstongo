"""
Unit tests for GST Filing app.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from apps.users.models import User, UserProfile
from apps.gst_filing.models import GSTFiling, GSTR1Details, GSTR3BDetails, Invoice


class GSTFilingModelTests(TestCase):
    """Test cases for GSTFiling model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            email='filing_test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_gst_filing(self):
        """Test creating a GST filing."""
        filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
        
        self.assertEqual(filing.filing_type, 'GSTR1')
        self.assertEqual(filing.status, 'draft')
        self.assertEqual(filing.user, self.user)
    
    def test_filing_str_representation(self):
        """Test filing string representation."""
        filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
        
        expected = f"GSTR1 - filing_test@example.com - 2024-25 - 10"
        self.assertEqual(str(filing), expected)
    
    def test_mark_as_filed(self):
        """Test marking filing as filed."""
        filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR3B',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='pending'
        )
        
        filing.mark_as_filed('ABC123')
        
        self.assertEqual(filing.status, 'filed')
        self.assertEqual(filing.filing_reference_number, 'ABC123')
        self.assertIsNotNone(filing.filed_at)
    
    def test_nil_filing(self):
        """Test nil filing flag."""
        filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft',
            nil_filing=True
        )
        
        self.assertTrue(filing.nil_filing)
    
    def test_filing_lock(self):
        """Test filing lock functionality."""
        filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='pending'
        )
        
        filing.filing_locked = True
        filing.lock_reason = 'Under review'
        filing.save()
        
        self.assertTrue(filing.filing_locked)
        self.assertEqual(filing.lock_reason, 'Under review')
    
    def test_calculate_totals(self):
        """Test calculate totals from invoices."""
        filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
        
        # Create invoices
        Invoice.objects.create(
            filing=filing,
            invoice_number='INV001',
            invoice_date='2024-10-15',
            invoice_type='b2b',
            taxable_value=Decimal('10000.00'),
            igst=Decimal('1800.00'),
            total_tax=Decimal('1800.00')
        )
        Invoice.objects.create(
            filing=filing,
            invoice_number='INV002',
            invoice_date='2024-10-16',
            invoice_type='b2b',
            taxable_value=Decimal('20000.00'),
            igst=Decimal('3600.00'),
            total_tax=Decimal('3600.00')
        )
        
        # Calculate totals
        filing.calculate_totals()
        
        self.assertEqual(filing.total_taxable_value, Decimal('30000.00'))
        self.assertEqual(filing.total_tax, Decimal('5400.00'))


class GSTFilingAPITests(APITestCase):
    """Test cases for GST Filing API endpoints."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='api_filing@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_filing(self):
        """Test creating a new filing."""
        url = reverse('gst-filings-list')
        data = {
            'filing_type': 'GSTR1',
            'financial_year': '2024-25',
            'month': 10,
            'year': 2024,
            'nil_filing': False
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['filing_type'], 'GSTR1')
        self.assertEqual(response.data['status'], 'draft')
    
    def test_create_duplicate_filing_fails(self):
        """Test that duplicate filing creation fails."""
        url = reverse('gst-filings-list')
        data = {
            'filing_type': 'GSTR1',
            'financial_year': '2024-25',
            'month': 10,
            'year': 2024
        }
        
        # Create first filing
        self.client.post(url, data, format='json')
        
        # Try to create duplicate
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_filings(self):
        """Test listing user filings."""
        # Create some filings
        GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
        GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR3B',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='filed'
        )
        
        url = reverse('gst-filings-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_filings_by_type(self):
        """Test filtering filings by type."""
        # Create filings
        GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
        GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR3B',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
        
        url = reverse('gst-filings-list')
        response = self.client.get(url, {'filing_type': 'GSTR1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['filing_type'], 'GSTR1')
    
    def test_get_filing_detail(self):
        """Test getting filing detail."""
        filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
        
        url = reverse('gst-filings-detail', args=[filing.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['filing_type'], 'GSTR1')
    
    def test_nil_filing_declaration(self):
        """Test marking filing as nil with declaration."""
        filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
        
        url = reverse('gst-filings-mark-nil', args=[filing.id])
        data = {
            'declaration_statement': 'I declare that there are no transactions for this period.'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        filing.refresh_from_db()
        self.assertTrue(filing.nil_filing)
        self.assertTrue(filing.declaration_signed)
        self.assertEqual(filing.status, 'pending')


class InvoiceModelTests(TestCase):
    """Test cases for Invoice model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='invoice_test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.filing = GSTFiling.objects.create(
            user=self.user,
            filing_type='GSTR1',
            financial_year='2024-25',
            month=10,
            year=2024,
            status='draft'
        )
    
    def test_create_invoice(self):
        """Test creating an invoice."""
        invoice = Invoice.objects.create(
            filing=self.filing,
            invoice_number='INV001',
            invoice_date='2024-10-15',
            invoice_type='b2b',
            taxable_value=Decimal('10000.00'),
            igst=Decimal('1800.00'),
            cgst=Decimal('0.00'),
            sgst=Decimal('0.00'),
            total_tax=Decimal('1800.00')
        )
        
        self.assertEqual(invoice.invoice_number, 'INV001')
        self.assertEqual(invoice.taxable_value, Decimal('10000.00'))
        self.assertEqual(invoice.total_tax, Decimal('1800.00'))
    
    def test_invoice_types(self):
        """Test different invoice types."""
        invoice_types = ['b2b', 'b2c', 'export', 'debit_note', 'credit_note']
        
        for invoice_type in invoice_types:
            invoice = Invoice.objects.create(
                filing=self.filing,
                invoice_number=f'INV_{invoice_type}',
                invoice_date='2024-10-15',
                invoice_type=invoice_type,
                taxable_value=Decimal('5000.00'),
                total_tax=Decimal('900.00')
            )
            self.assertEqual(invoice.invoice_type, invoice_type)
