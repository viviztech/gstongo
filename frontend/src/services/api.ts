/**
 * API Service for GSTONGO Frontend
 */
import axios, { AxiosInstance, AxiosError } from "axios";
import { toast } from "react-hot-toast";

/**
 * Must be defined in .env as:
 * VITE_BACKEND_URL=https://gstongo.com
 */
// Normalize URL: remove trailing slashes
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL?.replace(/\/+$/, "");

// Hard fail if missing
if (!API_BASE_URL) {
  throw new Error("❌ VITE_BACKEND_URL is missing in .env");
}

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL.includes("/api")
    ? `${API_BASE_URL}/v1/`
    : `${API_BASE_URL}/api/v1/`,
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

        const refreshURL = API_BASE_URL.endsWith("/api")
          ? `${API_BASE_URL}/v1/auth/token/refresh/`
          : `${API_BASE_URL}/api/v1/auth/token/refresh/`;

        const response = await axios.post(refreshURL, { refresh: refreshToken });

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
      (error.response?.data as any)?.detail ||
      error.message ||
      "An unexpected error occurred. Please try again later.";

    toast.error(message);
    return Promise.reject(error);
  }
);

/* ===================== AUTH ===================== */

export const authAPI = {
  register: (data: any) => api.post("auth/register/", data),
  login: (email: string, password: string) =>
    api.post("auth/login/", { email, password }),
  refreshToken: (refresh: string) =>
    api.post("auth/token/refresh/", { refresh }),
  getProfile: () => api.get("auth/profile/"),
  forgotPassword: (email: string) =>
    api.post("auth/password/request_reset/", { email }),
  verifyResetToken: (token: string) =>
    api.post("auth/password/verify_token/", { token }),
  resetPassword: (token: string, newPassword: string, newPasswordConfirm: string) =>
    api.post("auth/password/confirm_reset/", { token, new_password: newPassword, new_password_confirm: newPasswordConfirm }),
};

/* ===================== GST ===================== */

export const gstFilingAPI = {
  getFilings: (params?: any) => api.get("gst/filings/", { params }),
  getFiling: (id: string) => api.get(`gst/filings/${id}/`),
  createFiling: (data: any) => api.post("gst/filings/", data),
  getFilingSummary: (id: string) => api.get(`gst/filings/${id}/summary/`),
  declareFiling: (id: string) => api.post(`gst/filings/${id}/declare/`),
  markNilFiling: (id: string, data: any) => api.post(`gst/filings/${id}/mark_nil/`, data),
  uploadInvoices: (filingId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post(`gst/filings/${filingId}/upload_invoices/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  downloadTemplateFile: (type: string, financialYear: string) => {
    const base = API_BASE_URL.includes("/api")
      ? `${API_BASE_URL}/v1`
      : `${API_BASE_URL}/api/v1`;
    return `${base}/gst/filings/download_template/?type=${type}&financial_year=${financialYear}`;
  },
};

/* ===================== INVOICES ===================== */

export const invoiceAPI = {
  getInvoices: (params?: any) => api.get("invoices/invoices/", { params }),
  getInvoice: (id: string) => api.get(`invoices/invoices/${id}/`),
  initiatePayment: (invoiceId: string) =>
    api.post("invoices/payments/initiate/", { invoice_id: invoiceId }),
};



// ---------------- USER ----------------
export const userAPI = {
  getProfile: () => api.get("auth/profile/"),

  updateProfile: (data: any) =>
    api.patch("auth/profile/", data),

  getNotifications: () =>
    api.get("notifications/list/"),

  markNotificationRead: (id: string) =>
    api.post(`notifications/list/${id}/mark_as_read/`),

  getUnreadCount: () =>
    api.get("notifications/list/unread_count/"),

  changePassword: (data: any) =>
    api.post("auth/password/change/", data),
};


export default api;
