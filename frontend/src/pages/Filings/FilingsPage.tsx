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
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { gstFilingAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import toast from 'react-hot-toast';

const FILING_TYPES = [
  { value: 'GSTR1', label: 'GSTR-1 (Outward Supplies)' },
  { value: 'GSTR3B', label: 'GSTR-3B (Summary Return)' },
  { value: 'GSTR9B', label: 'GSTR-9B (Annual Return)' },
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
  const [newFiling, setNewFiling] = useState({
    filing_type: 'GSTR1',
    financial_year: '2024-25',
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
    switch (status) {
      case 'filed': return 'bg-green-100 text-green-700';
      case 'pending': return 'bg-yellow-100 text-yellow-700';
      case 'rejected': return 'bg-red-100 text-red-700';
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
          <h1 className="text-2xl font-bold text-gray-900">GST Filings</h1>
          <p className="text-gray-600 mt-1">Manage your GST return filings</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          New Filing
        </button>
      </div>
      
      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filing Type
            </label>
            <select
              value={filter.filing_type}
              onChange={(e) => setFilter({ ...filter, filing_type: e.target.value })}
              className="input-field"
            >
              <option value="">All Types</option>
              {FILING_TYPES.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filter.status}
              onChange={(e) => setFilter({ ...filter, status: e.target.value })}
              className="input-field"
            >
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="pending">Pending</option>
              <option value="filed">Filed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Filings List */}
      <div className="card">
        {filings?.data?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Type</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Period</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Nil Filing</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Date</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">Action</th>
                </tr>
              </thead>
              <tbody>
                {(filings?.data || []).map((filing: any) => (
                  <tr key={filing.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center">
                        <DocumentTextIcon className="w-5 h-5 text-primary-600 mr-2" />
                        <span className="font-medium">{filing.filing_type}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {MONTHS.find(m => m.value === filing.month)?.label} {filing.year}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(filing.status)}`}>
                        {filing.status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {filing.nil_filing ? (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">Nil</span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {new Date(filing.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/filings/${filing.id}`}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <DocumentTextIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No Filings Found</h3>
            <p className="text-gray-500 mb-4">Get started by creating your first GST filing</p>
            <button
              onClick={() => setShowModal(true)}
              className="btn-primary"
            >
              Create Filing
            </button>
          </div>
        )}
      </div>
      
      {/* Create Filing Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
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
                  <option value="2024-25">2024-25</option>
                  <option value="2025-26">2025-26</option>
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
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="nil_filing"
                  checked={newFiling.nil_filing}
                  onChange={(e) => setNewFiling({ ...newFiling, nil_filing: e.target.checked })}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded"
                />
                <label htmlFor="nil_filing" className="ml-2 text-sm text-gray-700">
                  Mark as Nil Return (no transactions)
                </label>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
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
