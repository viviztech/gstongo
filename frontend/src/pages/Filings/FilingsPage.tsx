/**
 * Filings Page Component
 */
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  DocumentTextIcon,
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';
import { gstFilingAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import toast from 'react-hot-toast';

const FILING_TYPES = [
  { value: 'GSTR1', label: 'GSTR-1' },
  { value: 'GSTR3B', label: 'GSTR-3B' },
  { value: 'GSTR9B', label: 'GSTR-9B' },
];

const MONTHS = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' },
];

const FilingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState({ filing_type: '', status: '' });
  const [searchTerm, setSearchTerm] = useState('');

  const getCurrentFinancialYear = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth() + 1;

    if (month >= 4) {
      return `${year}-${(year + 1).toString().slice(-2)}`;
    } else {
      return `${year - 1}-${year.toString().slice(-2)}`;
    }
  };

  const getFinancialYearOptions = () => {
    const currentFY = getCurrentFinancialYear();
    const [startYear] = currentFY.split('-');
    const prevYear = parseInt(startYear) - 1;
    const nextYear = parseInt(startYear) + 1;

    return [
      { value: `${prevYear}-${startYear.slice(-2)}`, label: `${prevYear}-${startYear.slice(-2)}` },
      { value: currentFY, label: currentFY },
      { value: `${nextYear}-${(nextYear + 1).toString().slice(-2)}`, label: `${nextYear}-${(nextYear + 1).toString().slice(-2)}` },
    ];
  };

  const [newFiling, setNewFiling] = useState({
    filing_type: 'GSTR1',
    financial_year: getCurrentFinancialYear(),
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    nil_filing: false,
  });

  const { data: filings, isLoading, refetch } = useQuery({
    queryKey: ['filings', filter],
    queryFn: () => gstFilingAPI.getFilings(filter),
  });

  const createFilingMutation = useMutation({
    mutationFn: (data: any) => gstFilingAPI.createFiling(data),
    onSuccess: (response) => {
      toast.success('Filing created successfully!');
      setShowModal(false);
      navigate(`/filings/${response.data.id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Failed to create filing');
    },
  });

  const handleCreateFiling = () => {
    createFilingMutation.mutate(newFiling);
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      filed: 'bg-green-100 text-green-700',
      pending: 'bg-yellow-100 text-yellow-700',
      rejected: 'bg-red-100 text-red-700',
      draft: 'bg-gray-100 text-gray-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const filingsList = Array.isArray(filings?.data)
    ? filings.data
    : (Array.isArray(filings?.data?.results) ? filings.data.results : []);

  // Calculate stats from visible list (or ideally from API)
  const totalFilings = filingsList.length;
  const pendingFilings = filingsList.filter((f: any) => f.status === 'pending' || f.status === 'draft').length;
  const filedFilings = filingsList.filter((f: any) => f.status === 'filed').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">GST Return Filings</h1>
          <p className="text-gray-600 mt-1">Manage and track your GSTR-1, GSTR-3B filings</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <PlusIcon className="w-5 h-5" />
          Create New Filing
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Filings</p>
              <p className="text-2xl font-bold">{totalFilings}</p>
            </div>
            <DocumentTextIcon className="w-10 h-10 text-blue-200" />
          </div>
        </div>
        <div className="card bg-gradient-to-br from-yellow-500 to-orange-500 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Pending / Draft</p>
              <p className="text-2xl font-bold">{pendingFilings}</p>
            </div>
            <ClockIcon className="w-10 h-10 text-yellow-200" />
          </div>
        </div>
        <div className="card bg-gradient-to-br from-green-500 to-emerald-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Successfully Filed</p>
              <p className="text-2xl font-bold">{filedFilings}</p>
            </div>
            <CheckCircleIcon className="w-10 h-10 text-green-200" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search filings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center gap-2">
            <FunnelIcon className="w-5 h-5 text-gray-400" />
            <select
              value={filter.filing_type}
              onChange={(e) => setFilter({ ...filter, filing_type: e.target.value })}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Types</option>
              {FILING_TYPES.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
            <select
              value={filter.status}
              onChange={(e) => setFilter({ ...filter, status: e.target.value })}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="pending">Pending</option>
              <option value="filed">Filed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Filings List */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          {filingsList.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left py-3 px-6 text-xs font-medium text-gray-500 uppercase">Filing Type</th>
                  <th className="text-left py-3 px-6 text-xs font-medium text-gray-500 uppercase">Period</th>
                  <th className="text-left py-3 px-6 text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="text-left py-3 px-6 text-xs font-medium text-gray-500 uppercase">Nil Return</th>
                  <th className="text-left py-3 px-6 text-xs font-medium text-gray-500 uppercase">Created Date</th>
                  <th className="text-right py-3 px-6 text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filingsList.map((filing: any) => (
                  <tr key={filing.id} className="hover:bg-gray-50 transition-colors">
                    <td className="py-4 px-6">
                      <div className="flex items-center">
                        <div className="p-2 bg-primary-50 rounded-lg mr-3">
                          <DocumentTextIcon className="w-5 h-5 text-primary-600" />
                        </div>
                        <span className="font-medium text-gray-900">{filing.filing_type}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-gray-600">
                      {MONTHS.find(m => m.value === filing.month)?.label} {filing.year}
                    </td>
                    <td className="py-4 px-6">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(filing.status)}`}>
                        {filing.status.charAt(0).toUpperCase() + filing.status.slice(1)}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      {filing.nil_filing ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          YES
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-sm text-gray-600">
                      {new Date(filing.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-6 text-right">
                      <Link
                        to={`/filings/${filing.id}`}
                        className="text-primary-600 hover:text-primary-800 font-medium text-sm"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <DocumentTextIcon className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-1">No Filings Found</h3>
              <p className="text-gray-500 mb-6 max-w-sm mx-auto">
                You haven't created any GST filings yet. Start by creating a new filing for the current period.
              </p>
              <button
                onClick={() => setShowModal(true)}
                className="btn-primary"
              >
                Create First Filing
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Create Filing Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4 animate-fadeIn">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Create New Filing</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filing Type
                </label>
                <select
                  value={newFiling.filing_type}
                  onChange={(e) => setNewFiling({ ...newFiling, filing_type: e.target.value })}
                  className="input-field"
                >
                  {FILING_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Financial Year
                </label>
                <select
                  value={newFiling.financial_year}
                  onChange={(e) => setNewFiling({ ...newFiling, financial_year: e.target.value })}
                  className="input-field"
                >
                  {getFinancialYearOptions().map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Month
                </label>
                <select
                  value={newFiling.month}
                  onChange={(e) => setNewFiling({ ...newFiling, month: parseInt(e.target.value) })}
                  className="input-field"
                >
                  {MONTHS.map((month) => (
                    <option key={month.value} value={month.value}>{month.label}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center p-3 bg-gray-50 rounded-lg border border-gray-200">
                <input
                  type="checkbox"
                  id="nil_filing"
                  checked={newFiling.nil_filing}
                  onChange={(e) => setNewFiling({ ...newFiling, nil_filing: e.target.checked })}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <label htmlFor="nil_filing" className="ml-3 text-sm font-medium text-gray-700 cursor-pointer">
                  Mark as Nil Return
                  <span className="block text-xs text-gray-500 font-normal">Select this if you have no transactions for this period</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-8">
              <button
                onClick={() => setShowModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateFiling}
                disabled={createFilingMutation.isPending}
                className="btn-primary"
              >
                {createFilingMutation.isPending ? 'Creating...' : 'Create Filing'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilingsPage;
