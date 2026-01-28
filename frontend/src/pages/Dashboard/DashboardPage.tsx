/**
 * Dashboard Page Component
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  DocumentTextIcon,
  CheckCircleIcon,
  ClockIcon,
  CurrencyRupeeIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';
import { userAPI, gstFilingAPI, invoiceAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  color: 'blue' | 'green' | 'yellow' | 'red';
  trend?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, color, trend }) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    red: 'bg-red-50 text-red-600',
  };
  
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <p className="text-sm text-green-600 mt-1 flex items-center">
              <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />
              {trend}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};

const DashboardPage: React.FC = () => {
  const { data: profile, isLoading: profileLoading, isError: profileError } = useQuery({
    queryKey: ['profile'],
    queryFn: () => userAPI.getProfile(),
  });

  const { data: filings, isLoading: filingsLoading, isError: filingsError } = useQuery({
    queryKey: ['filings'],
    queryFn: () => gstFilingAPI.getFilings(),
  });

  const { data: invoices, isLoading: invoicesLoading, isError: invoicesError } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => invoiceAPI.getInvoices(),
  });

  const isLoading = profileLoading || filingsLoading || invoicesLoading;
  const hasError = profileError || filingsError || invoicesError;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <p className="text-red-600 mb-4">Failed to load dashboard data</p>
        <button
          onClick={() => window.location.reload()}
          className="btn-primary"
        >
          Retry
        </button>
      </div>
    );
  }
  
  // Profile API returns an array, get the first item
  const userData = Array.isArray(profile?.data) ? profile?.data[0] : profile?.data;
  const filingList = Array.isArray(filings?.data) ? filings.data : [];
  const invoiceList = invoices?.data?.invoices || [];
  
  // Calculate stats
  const totalFilings = filingList.length;
  const pendingFilings = filingList.filter((f: any) => f.status === 'pending').length;
  const filedFilings = filingList.filter((f: any) => f.status === 'filed').length;
  const pendingAmount = invoiceList
    .filter((i: any) => i.status !== 'paid')
    .reduce((sum: number, i: any) => sum + parseFloat(i.total_amount || 0), 0);
  
  // Recent filings
  const recentFilings = filingList.slice(0, 5);
  
  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {userData?.first_name || 'User'}!
          </h1>
          <p className="text-gray-600 mt-1">
            Here's what's happening with your GST filings
          </p>
        </div>
        <Link to="/filings" className="btn-primary">
          New Filing
        </Link>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Filings"
          value={totalFilings}
          icon={DocumentTextIcon}
          color="blue"
        />
        <StatCard
          title="Pending"
          value={pendingFilings}
          icon={ClockIcon}
          color="yellow"
        />
        <StatCard
          title="Filed"
          value={filedFilings}
          icon={CheckCircleIcon}
          color="green"
        />
        <StatCard
          title="Pending Payment"
          value={`₹${pendingAmount.toLocaleString()}`}
          icon={CurrencyRupeeIcon}
          color="red"
        />
      </div>
      
      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Filings */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Filings</h2>
            <Link to="/filings" className="text-sm text-primary-600 hover:text-primary-700">
              View All
            </Link>
          </div>
          
          {recentFilings.length > 0 ? (
            <div className="space-y-3">
              {recentFilings.map((filing: any) => (
                <Link
                  key={filing.id}
                  to={`/filings/${filing.id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      filing.status === 'filed' ? 'bg-green-100 text-green-600' :
                      filing.status === 'pending' ? 'bg-yellow-100 text-yellow-600' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      <DocumentTextIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{filing.filing_type}</p>
                      <p className="text-sm text-gray-500">
                        {filing.month}/{filing.year} - {filing.financial_year}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    filing.status === 'filed' ? 'bg-green-100 text-green-700' :
                    filing.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {filing.status}
                  </span>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <DocumentTextIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No filings yet</p>
              <Link to="/filings" className="text-primary-600 hover:text-primary-700 text-sm">
                Start your first filing
              </Link>
            </div>
          )}
        </div>
        
        {/* Quick Actions */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <Link
              to="/filings"
              className="p-4 rounded-lg border-2 border-dashed border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors text-center"
            >
              <DocumentTextIcon className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <p className="font-medium text-gray-700">New Filing</p>
              <p className="text-sm text-gray-500">Start GSTR filing</p>
            </Link>
            <Link
              to="/invoices"
              className="p-4 rounded-lg border-2 border-dashed border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors text-center"
            >
              <CurrencyRupeeIcon className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <p className="font-medium text-gray-700">Pay Invoice</p>
              <p className="text-sm text-gray-500">View pending payments</p>
            </Link>
            <Link
              to="/profile"
              className="p-4 rounded-lg border-2 border-dashed border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors text-center"
            >
              <DocumentTextIcon className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <p className="font-medium text-gray-700">Update Profile</p>
              <p className="text-sm text-gray-500">Manage your details</p>
            </Link>
            <Link
              to="/filings"
              className="p-4 rounded-lg border-2 border-dashed border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors text-center"
            >
              <DocumentTextIcon className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <p className="font-medium text-gray-700">Download Template</p>
              <p className="text-sm text-gray-500">Get filing templates</p>
            </Link>
          </div>
        </div>
      </div>
      
      {/* Upcoming Deadlines */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Deadlines</h2>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <ClockIcon className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
            <div>
              <p className="font-medium text-yellow-800">GSTR-1 Filing Due</p>
              <p className="text-sm text-yellow-700 mt-1">
                Remember to file your GSTR-1 for the current month by the 11th of next month.
              </p>
            </div>
          </div>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-3">
          <div className="flex items-start">
            <ClockIcon className="w-5 h-5 text-blue-600 mt-0.5 mr-3" />
            <div>
              <p className="font-medium text-blue-800">GSTR-3B Filing Due</p>
              <p className="text-sm text-blue-700 mt-1">
                GSTR-3B for the current month is due by the 20th of next month.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
