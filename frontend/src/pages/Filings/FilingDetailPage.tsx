/**
 * Filing Detail Page Component
 */
import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  ArrowLeftIcon,
  DocumentTextIcon,
  PencilIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CloudArrowUpIcon,
  DocumentArrowDownIcon,
} from '@heroicons/react/24/outline';
import { gstFilingAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import toast from 'react-hot-toast';

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const FilingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { data: filing, isLoading, refetch } = useQuery({
    queryKey: ['filing', id],
    queryFn: () => gstFilingAPI.getFiling(id!),
    enabled: !!id,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => gstFilingAPI.uploadInvoices(id!, file),
    onSuccess: (response) => {
      toast.success(`${response.data.invoice_count} invoices uploaded successfully`);
      setShowUploadModal(false);
      setSelectedFile(null);
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Failed to upload invoices');
    },
  });

  const declareMutation = useMutation({
    mutationFn: () => gstFilingAPI.declareFiling(id!),
    onSuccess: () => {
      toast.success('Declaration submitted successfully');
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Failed to submit declaration');
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'filed': return 'bg-green-100 text-green-700';
      case 'pending': return 'bg-yellow-100 text-yellow-700';
      case 'rejected': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'filed': return <CheckCircleIcon className="w-6 h-6 text-green-600" />;
      case 'pending': return <ClockIcon className="w-6 h-6 text-yellow-600" />;
      case 'rejected': return <ExclamationTriangleIcon className="w-6 h-6 text-red-600" />;
      default: return <DocumentTextIcon className="w-6 h-6 text-gray-600" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!filing?.data) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Filing Not Found</h3>
        <Link to="/filings" className="text-primary-600 hover:text-primary-700">
          Back to Filings
        </Link>
      </div>
    );
  }

  const filingData = filing.data;
  const filingDetails = filingData.details || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/filings')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeftIcon className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {filingData.filing_type} Filing
            </h1>
            <p className="text-gray-600">
              {MONTHS[filingData.month - 1]} {filingData.year} - {filingData.financial_year}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(filingData.status)}`}>
            {filingData.status}
          </span>
          {filingData.nil_filing && (
            <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700">
              Nil Return
            </span>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => setShowUploadModal(true)}
          disabled={filingData.filing_locked || filingData.status === 'filed'}
          className="card p-4 flex items-center space-x-3 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="p-2 bg-blue-100 rounded-lg">
            <CloudArrowUpIcon className="w-6 h-6 text-blue-600" />
          </div>
          <div className="text-left">
            <p className="font-medium text-gray-900">Upload Invoices</p>
            <p className="text-sm text-gray-500">Upload Excel file with invoice data</p>
          </div>
        </button>

        <Link
          to={`/filings/${id}/template`}
          className="card p-4 flex items-center space-x-3 hover:bg-gray-50"
        >
          <div className="p-2 bg-green-100 rounded-lg">
            <DocumentArrowDownIcon className="w-6 h-6 text-green-600" />
          </div>
          <div className="text-left">
            <p className="font-medium text-gray-900">Download Template</p>
            <p className="text-sm text-gray-500">Get Excel template for filing</p>
          </div>
        </Link>

        {filingData.status === 'draft' && !filingData.nil_filing && (
          <button
            onClick={() => declareMutation.mutate()}
            disabled={declareMutation.isPending}
            className="card p-4 flex items-center space-x-3 hover:bg-gray-50 disabled:opacity-50"
          >
            <div className="p-2 bg-purple-100 rounded-lg">
              <PencilIcon className="w-6 h-6 text-purple-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Submit Declaration</p>
              <p className="text-sm text-gray-500">File your return with declaration</p>
            </div>
          </button>
        )}
      </div>

      {/* Filing Summary */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filing Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-500">Total Taxable Value</p>
            <p className="text-xl font-bold text-gray-900">
              ₹{parseFloat(filingData.total_taxable_value || 0).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Total Tax</p>
            <p className="text-xl font-bold text-gray-900">
              ₹{parseFloat(filingData.total_tax || 0).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Invoice Count</p>
            <p className="text-xl font-bold text-gray-900">
              {filingDetails.invoice_count || 0}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Filing Reference</p>
            <p className="text-xl font-bold text-gray-900">
              {filingData.filing_reference_number || '-'}
            </p>
          </div>
        </div>
      </div>

      {/* GSTR-1 Details */}
      {filingData.filing_type === 'GSTR1' && filingDetails && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">GSTR-1 Details</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">B2B Invoices</p>
              <p className="font-medium text-gray-900">
                {filingDetails.b2b_invoices_count || 0}
              </p>
              <p className="text-xs text-gray-500">
                ₹{parseFloat(filingDetails.b2b_invoices_value || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">B2C Invoices</p>
              <p className="font-medium text-gray-900">
                {filingDetails.b2c_invoices_count || 0}
              </p>
              <p className="text-xs text-gray-500">
                ₹{parseFloat(filingDetails.b2c_invoices_value || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Exports</p>
              <p className="font-medium text-gray-900">
                {filingDetails.export_invoices_count || 0}
              </p>
              <p className="text-xs text-gray-500">
                ₹{parseFloat(filingDetails.export_value || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Credit/Debit Notes</p>
              <p className="font-medium text-gray-900">
                C: {filingDetails.credit_notes_count || 0} / D: {filingDetails.debit_notes_count || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* GSTR-3B Details */}
      {filingData.filing_type === 'GSTR3B' && filingDetails && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">GSTR-3B Details</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">Outward Supplies</p>
              <p className="font-medium text-gray-900">
                ₹{parseFloat(filingDetails.outward_taxable_supplies || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">ITC Claimed</p>
              <p className="font-medium text-gray-900">
                ₹{parseFloat(filingDetails.total_itc_claimed || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Tax Liability (IGST)</p>
              <p className="font-medium text-gray-900">
                ₹{parseFloat(filingDetails.igst_liability || 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Interest Payable</p>
              <p className="font-medium text-gray-900">
                ₹{parseFloat(filingDetails.interest_payable || 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Declaration Status */}
      {filingData.declaration_signed && (
        <div className="card bg-green-50 border-green-200">
          <div className="flex items-center space-x-3">
            <CheckCircleIcon className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-medium text-green-800">Declaration Submitted</p>
              <p className="text-sm text-green-700">
                Filed on {new Date(filingData.declaration_signed_at).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Filing Locked Warning */}
      {filingData.filing_locked && (
        <div className="card bg-yellow-50 border-yellow-200">
          <div className="flex items-center space-x-3">
            <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600" />
            <div>
              <p className="font-medium text-yellow-800">Filing is Locked</p>
              <p className="text-sm text-yellow-700">
                Reason: {filingData.lock_reason || 'Locked by admin'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Invoices</h2>
            
            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600 mb-2">
                  Upload Excel file with invoice data
                </p>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="text-sm"
                />
              </div>
              
              {selectedFile && (
                <p className="text-sm text-gray-600">
                  Selected: {selectedFile.name}
                </p>
              )}
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setSelectedFile(null);
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => selectedFile && uploadMutation.mutate(selectedFile)}
                disabled={!selectedFile || uploadMutation.isPending}
                className="btn-primary"
              >
                {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilingDetailPage;
