/**
 * Admin Dashboard Page Component
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

const AdminDashboardPage: React.FC = () => {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => adminAPI.getDashboard(),
  });
  
  const { data: filingReport } = useQuery({
    queryKey: ['filing-report'],
    queryFn: () => adminAPI.getFilingReport(),
  });
  
  const { data: paymentReport } = useQuery({
    queryKey: ['payment-report'],
    queryFn: () => adminAPI.getPaymentReport(),
  });
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  const stats = dashboard?.data || {};
  const filings = filingReport?.data || [];
  const payments = paymentReport?.data || {};
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-600">Total Users</p>
          <p className="text-3xl font-bold text-gray-900">{stats.total_users || 0}</p>
          <p className="text-sm text-green-600">
            +{stats.new_users_today || 0} today
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Pending Filings</p>
          <p className="text-3xl font-bold text-yellow-600">{stats.pending_filings || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Collected This Month</p>
          <p className="text-3xl font-bold text-green-600">
            ₹{(stats.total_collected || 0).toLocaleString()}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Overdue Amount</p>
          <p className="text-3xl font-bold text-red-600">
            ₹{(stats.overdue_amount || 0).toLocaleString()}
          </p>
          <p className="text-sm text-red-500">
            {stats.overdue_count || 0} invoices
          </p>
        </div>
      </div>
      
      {/* Filing Report */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filing Statistics</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4">Filing Type</th>
                <th className="text-right py-2 px-4">Total</th>
                <th className="text-right py-2 px-4">Filed</th>
                <th className="text-right py-2 px-4">Pending</th>
                <th className="text-right py-2 px-4">Nil</th>
              </tr>
            </thead>
            <tbody>
              {filings.map((filing: any) => (
                <tr key={filing.filing_type} className="border-b">
                  <td className="py-2 px-4">{filing.filing_type}</td>
                  <td className="py-2 px-4 text-right">{filing.total_count}</td>
                  <td className="py-2 px-4 text-right text-green-600">{filing.filed_count}</td>
                  <td className="py-2 px-4 text-right text-yellow-600">{filing.pending_count}</td>
                  <td className="py-2 px-4 text-right">{filing.nil_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Payment Report */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Summary</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Invoiced</span>
              <span className="font-medium">₹{(payments.total_invoiced || 0).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Total Collected</span>
              <span className="font-medium text-green-600">₹{(payments.total_collected || 0).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Pending Amount</span>
              <span className="font-medium text-yellow-600">₹{(payments.pending_amount || 0).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Collection Rate</span>
              <span className="font-medium">{payments.collection_rate || 0}%</span>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-2">
            <button className="w-full btn-secondary text-left">
              Search Users
            </button>
            <button className="w-full btn-secondary text-left">
              View Activity Logs
            </button>
            <button className="w-full btn-secondary text-left">
              Manage Rate Slabs
            </button>
            <button className="w-full btn-secondary text-left">
              Send Bulk Notifications
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;
