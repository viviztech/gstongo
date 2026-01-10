/**
 * API Service for GSTONGO Frontend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import { toast } from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    // Handle 401 errors - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          
          const { access } = response.data;
          localStorage.setItem('accessToken', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        toast.error('Session expired. Please login again.');
      }
    }
    
    // Show error toast
    const message = (error.response?.data as any)?.error?.message || 
                   error.message || 
                   'An error occurred';
    toast.error(message);
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: {
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    phone_number?: string;
  }) => api.post('/auth/register/', data),
  
  login: (email: string, password: string) => 
    api.post('/auth/login/', { email, password }),
  
  sendOTP: (method: 'email' | 'phone', email?: string, phone?: string) =>
    api.post('/auth/otp/send/', { method, email, phone }),
  
  verifyOTP: (otp: string, method: 'email' | 'phone', email?: string, phone?: string) =>
    api.post('/auth/otp/verify/', { otp, method, email, phone }),
  
  changePassword: (oldPassword: string, newPassword: string) =>
    api.post('/auth/password/change/', { old_password: oldPassword, new_password: newPassword }),
  
  refreshToken: (refresh: string) =>
    api.post('/auth/token/refresh/', { refresh }),
};

// User API
export const userAPI = {
  getProfile: () => api.get('/auth/profile/'),
  
  updateProfile: (data: any) => api.patch('/auth/profile/', data),
  
  getNotifications: () => api.get('/notifications/list/'),
  
  markNotificationRead: (id: string) => 
    api.post(`/notifications/list/${id}/mark_as_read/`),
  
  getUnreadCount: () => api.get('/notifications/list/unread_count/'),
};

// GST Filing API
export const gstFilingAPI = {
  getFilings: (params?: {
    filing_type?: string;
    status?: string;
    financial_year?: string;
  }) => api.get('/gst/filings/', { params }),
  
  getFiling: (id: string) => api.get(`/gst/filings/${id}/`),
  
  createFiling: (data: {
    filing_type: string;
    financial_year: string;
    month: number;
    year: number;
    nil_filing?: boolean;
  }) => api.post('/gst/filings/', data),
  
  uploadInvoices: (filingId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/gst/filings/${filingId}/upload_invoices/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  submitDeclaration: (filingId: string, declaration: string) =>
    api.post(`/gst/filings/${filingId}/declare/`, { declaration_statement: declaration }),
  
  markNilReturn: (filingId: string, declaration: string) =>
    api.post(`/gst/filings/${filingId}/mark_nil/`, { declaration_statement: declaration }),
  
  getFilingSummary: (filingId: string) =>
    api.get(`/gst/filings/${filingId}/summary/`),
  
  downloadTemplate: (type: string, financialYear: string) =>
    api.get('/gst/filings/templates/', { params: { type, financial_year: financialYear } }),
};

// Invoice API
export const invoiceAPI = {
  getInvoices: (params?: { status?: string }) =>
    api.get('/invoices/invoices/', { params }),
  
  getInvoice: (id: string) => api.get(`/invoices/invoices/${id}/`),
  
  getProformaInvoices: (params?: { status?: string }) =>
    api.get('/invoices/proforma/', { params }),
  
  generateProforma: (filingId: string, invoiceCount: number) =>
    api.post('/invoices/proforma/generate/', { filing_id: filingId, invoice_count: invoiceCount }),
  
  convertProforma: (id: string) =>
    api.post(`/invoices/proforma/${id}/convert_to_invoice/`),
  
  initiatePayment: (invoiceId?: string, proformaId?: string, gateway: string = 'razorpay') =>
    api.post('/invoices/payments/initiate/', { invoice_id: invoiceId, proforma_id: proformaId, gateway }),
  
  getPaymentHistory: () => api.get('/invoices/payments/history/'),
};

// Admin API
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard/'),
  
  getFilingReport: () => api.get('/admin/dashboard/filing_report/'),
  
  getPaymentReport: () => api.get('/admin/dashboard/payment_report/'),
  
  searchUsers: (searchType: string, searchValue: string) =>
    api.post('/admin/search/search/', { search_type: searchType, search_value: searchValue }),
  
  updateFilingStatus: (filingId: string, status: string, reference?: string) =>
    api.post(`/admin/filing/${filingId}/update_status/`, { status, filing_reference_number: reference }),
  
  lockFiling: (filingId: string, reason: string) =>
    api.post(`/admin/filing/${filingId}/lock/`, { reason }),
  
  unlockFiling: (filingId: string) =>
    api.post(`/admin/filing/${filingId}/unlock/`),
  
  triggerReminder: (filingId: string) =>
    api.post(`/admin/filing/${filingId}/trigger_reminder/`),
  
  getCollectionSummary: () => api.get('/admin/payments/collection_summary/'),
  
  recordManualPayment: (invoiceId: string, amount: number, method: string, reference: string) =>
    api.post(`/admin/payments/${invoiceId}/record_manual_payment/`, { amount, method, reference }),
  
  getActivityLogs: (params?: {
    admin_id?: string;
    action?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/admin/activity/', { params }),
};

export default api;
