class ApiConfig {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  static const String wsUrl = 'ws://localhost:8000/ws';
  
  // Endpoints
  static const String login = '/auth/login/';
  static const String register = '/auth/register/';
  static const String logout = '/auth/logout/';
  static const String refreshToken = '/auth/token/refresh/';
  static const String verifyOTP = '/auth/verify-otp/';
  static const String sendOTP = '/auth/send-otp/';
  
  // GST Filing
  static const String filings = '/gst/filings/';
  static const String uploadExcel = '/gst/upload-excel/';
  static const String gstrTemplates = '/gst/templates/';
  
  // Invoices
  static const String invoices = '/invoices/';
  static const String proformaInvoices = '/invoices/proforma/';
  static const String initiatePayment = '/payments/initiate/';
  static const String verifyPayment = '/payments/verify/';
  
  // Notifications
  static const String notifications = '/notifications/';
  
  // Admin
  static const String dashboard = '/admin/dashboard/';
  static const String users = '/admin/users/';
  static const String rateSlabs = '/admin/rate-slabs/';
  static const String reports = '/admin/reports/';
}
