/**
 * API Service for GSTONGO Frontend
 */
import axios, { AxiosInstance, AxiosError } from "axios";
import { toast } from "react-hot-toast";

/**
 * Must be defined in .env as:
 * VITE_BACKEND_URL=http://51.21.196.208:8000
 */
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL;

// Hard fail if missing
if (!API_BASE_URL) {
  throw new Error("❌ VITE_BACKEND_URL is missing in .env");
}

/**
 * Axios instance
 * Backend root = http://51.21.196.208:8000
 * All API routes start with /api/v1
 */
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

/* ===================== REQUEST INTERCEPTOR ===================== */

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/* ===================== RESPONSE INTERCEPTOR ===================== */

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest: any = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) throw new Error("No refresh token");

        const response = await axios.post(
          `${API_BASE_URL}/api/v1/auth/token/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem("accessToken", access);
        originalRequest.headers.Authorization = `Bearer ${access}`;

        return api(originalRequest);
      } catch {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        window.location.href = "/login";
        toast.error("Session expired. Please login again.");
      }
    }

    const message =
      (error.response?.data as any)?.error?.message ||
      error.message ||
      "Something went wrong";

    toast.error(message);
    return Promise.reject(error);
  }
);

/* ===================== AUTH ===================== */

export const authAPI = {
  register: (data: any) => api.post("/auth/register/", data),
  login: (email: string, password: string) =>
    api.post("/auth/login/", { email, password }),
  refreshToken: (refresh: string) =>
    api.post("/auth/token/refresh/", { refresh }),
  getProfile: () => api.get("/auth/profile/"),
  forgotPassword: (email: string) =>
    api.post("/auth/password/request_reset/", { email }),
  verifyResetToken: (token: string) =>
    api.post("/auth/password/verify_token/", { token }),
  resetPassword: (token: string, newPassword: string, newPasswordConfirm: string) =>
    api.post("/auth/password/confirm_reset/", { token, new_password: newPassword, new_password_confirm: newPasswordConfirm }),
};

/* ===================== GST ===================== */

export const gstFilingAPI = {
  getFilings: (params?: any) => api.get("/gst/filings/", { params }),
  getFiling: (id: string) => api.get(`/gst/filings/${id}/`),
  createFiling: (data: any) => api.post("/gst/filings/", data),
  getFilingSummary: (id: string) => api.get(`/gst/filings/${id}/summary/`),
  declareFiling: (id: string) => api.post(`/gst/filings/${id}/declare/`),
  markNilFiling: (id: string, data: any) => api.post(`/gst/filings/${id}/mark_nil/`, data),
  uploadInvoices: (filingId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post(`/gst/filings/${filingId}/upload_invoices/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  downloadTemplateFile: (type: string, financialYear: string) =>
    `${API_BASE_URL}/api/v1/gst/filings/download_template/?type=${type}&financial_year=${financialYear}`,
};

/* ===================== INVOICES ===================== */

export const invoiceAPI = {
  getInvoices: (params?: any) => api.get("/invoices/", { params }),
  getInvoice: (id: string) => api.get(`/invoices/${id}/`),
  initiatePayment: (invoiceId: string) =>
    api.post("/payments/initiate/", { invoice_id: invoiceId }),
};

/* ===================== ADMIN ===================== */

export const adminAPI = {
  getDashboard: () => api.get("/admin/dashboard/"),
  getUsers: () => api.get("/admin/users/"),
  getFilings: () => api.get("/admin/filings/"),
  getPayments: () => api.get("/admin/payments/"),
};

// ---------------- USER ----------------
export const userAPI = {
  getProfile: () => api.get("/auth/profile/"),

  updateProfile: (data: any) =>
    api.patch("/auth/profile/", data),

  getNotifications: () =>
    api.get("/notifications/"),

  markNotificationRead: (id: string) =>
    api.post(`/notifications/${id}/mark_as_read/`),

  getUnreadCount: () =>
    api.get("/notifications/unread_count/"),
};


export default api;
