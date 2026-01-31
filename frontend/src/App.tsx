/**
 * Main App Component for GSTONGO
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Layouts
import MainLayout from './components/Layout/MainLayout';
import AuthLayout from './components/Layout/AuthLayout';

// Auth Pages
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import ForgotPasswordPage from './pages/Auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/Auth/ResetPasswordPage';

// Main Pages
import DashboardPage from './pages/Dashboard/DashboardPage';
import FilingsPage from './pages/Filings/FilingsPage';
import FilingDetailPage from './pages/Filings/FilingDetailPage';
import InvoicesPage from './pages/Invoices/InvoicesPage';
import ProfilePage from './pages/Profile/ProfilePage';
import AdminDashboardPage from './pages/Admin/AdminDashboardPage';

// Phase II Pages
import ITRFilingsPage from './pages/ITR/ITRFilingsPage';
import TDSFilingsPage from './pages/TDS/TDSFilingsPage';
import BusinessServicesPage from './pages/Services/BusinessServicesPage';
import DocumentVaultPage from './pages/Vault/DocumentVaultPage';

// Phase III Pages
import SupportPage from './pages/Support/SupportPage';

// Phase IV Pages
import AnalyticsPage from './pages/Analytics/AnalyticsPage';

// Components
import PrivateRoute from './components/Auth/PrivateRoute';
import LoadingSpinner from './components/Common/LoadingSpinner';

// Query client configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              iconTheme: {
                primary: '#10B981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#EF4444',
                secondary: '#fff',
              },
            },
          }}
        />

        <React.Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Auth Routes */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />
            </Route>

            {/* Protected Routes */}
            <Route
              element={
                <PrivateRoute>
                  <MainLayout />
                </PrivateRoute>
              }
            >
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />

              {/* GST Filings */}
              <Route path="/filings" element={<FilingsPage />} />
              <Route path="/filings/:id" element={<FilingDetailPage />} />

              {/* ITR Filings */}
              <Route path="/itr" element={<ITRFilingsPage />} />
              <Route path="/itr/:id" element={<ITRFilingsPage />} />

              {/* TDS Filings */}
              <Route path="/tds" element={<TDSFilingsPage />} />
              <Route path="/tds/:id" element={<TDSFilingsPage />} />

              {/* Business Services */}
              <Route path="/services" element={<BusinessServicesPage />} />
              <Route path="/services/:id" element={<BusinessServicesPage />} />

              {/* Document Vault */}
              <Route path="/vault" element={<DocumentVaultPage />} />

              {/* Invoices & Payments */}
              <Route path="/invoices" element={<InvoicesPage />} />

              {/* Support */}
              <Route path="/support" element={<SupportPage />} />

              {/* Analytics */}
              <Route path="/analytics" element={<AnalyticsPage />} />

              {/* Profile */}
              <Route path="/profile" element={<ProfilePage />} />

              {/* Admin Routes */}
              <Route
                path="/admin"
                element={
                  <PrivateRoute roles={['admin']}>
                    <AdminDashboardPage />
                  </PrivateRoute>
                }
              />
            </Route>

            {/* 404 Route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </React.Suspense>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
