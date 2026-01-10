/**
 * Invoices Page Component
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  CurrencyRupeeIcon, 
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { invoiceAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

const InvoicesPage: React.FC = () => {
  const { data: invoices, isLoading } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => invoiceAPI.getInvoices(),
  });
  
  const invoiceList = invoices?.data?.invoices || [];
  const pendingAmount = invoices?.data?.pending_amount || 0;
  const hasPending = invoices?.data?.has_pending_payments || false;
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid': return <CheckCircleIcon className="w-5 h-5 text-green-600" />;
      case 'issued': return <ClockIcon className="w-5 h-5 text-yellow-600" />;
      case 'overdue': return <ClockIcon className="w-5 h-5 text-red-600" />;
      default: return <DocumentTextIcon className="w-5 h-5 text-gray-600" />;
    }
  };
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-green-100 text-green-700';
      case 'issued': return 'bg-yellow-100 text-yellow-700';
      case 'overdue': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-gray-600 mt-1">Manage your invoices and payments</p>
        </div>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending Amount</p>
              <p className="text-2xl font-bold text-gray-900">₹{pendingAmount.toLocaleString()}</p>
            </div>
            <div className="p-3 bg-yellow-50 rounded-lg">
              <CurrencyRupeeIcon className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Invoices</p>
              <p className="text-2xl font-bold text-gray-900">{invoiceList.length}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <DocumentTextIcon className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Payment Status</p>
              <p className={`text-2xl font-bold ${hasPending ? 'text-red-600' : 'text-green-600'}`}>
                {hasPending ? 'Action Required' : 'All Clear'}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${hasPending ? 'bg-red-50' : 'bg-green-50'}`}>
              {getStatusIcon(hasPending ? 'overdue' : 'paid')}
            </div>
          </div>
        </div>
      </div>
      
      {/* Invoices List */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">All Invoices</h2>
        
        {invoiceList.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Invoice</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Amount</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Due Date</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Date</th>
                </tr>
              </thead>
              <tbody>
                {invoiceList.map((invoice: any) => (
                  <tr key={invoice.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center">
                        {getStatusIcon(invoice.status)}
                        <div className="ml-3">
                          <p className="font-medium">{invoice.invoice_number}</p>
                          <p className="text-sm text-gray-500">{invoice.service_type}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-medium">
                      ₹{parseFloat(invoice.total_amount).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(invoice.status)}`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm">
                      {invoice.due_date ? new Date(invoice.due_date).toLocaleDateString() : '-'}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {new Date(invoice.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <CurrencyRupeeIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No invoices found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InvoicesPage;
