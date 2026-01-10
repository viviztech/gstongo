/**
 * Filing Detail Page Component
 */
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  ArrowLeftIcon,
  DocumentArrowUpIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { gstFilingAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import toast from 'react-hot-toast';

const FilingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showDeclaration, setShowDeclaration] = useState(false);
  const [declaration, setDeclaration] = useState('');
  
  const { data: filing, isLoading, refetch } = useQuery({
    queryKey: ['filing', id],
    queryFn: () => gstFilingAPI.getFiling(id!),
    enabled: !!id,
  });
  
  const uploadMutation = useMutation({
    mutationFn: (file: File) => gstFilingAPI.uploadInvoices(id!, file),
    onSuccess: () => {
      toast.success('Invoices uploaded successfully!');
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Upload failed');
    },
  });
  
  const declarationMutation = useMutation({
    mutationFn: (decl: string) => gstFilingAPI.submitDeclaration(id!, decl),
    onSuccess: () => {
      toast.success('Declaration submitted successfully!');
      setShowDeclaration(false);
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Failed to submit declaration');
    },
  });
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        toast.error('Please upload an Excel file');
        return;
      }
      setSelectedFile(file);
    }
  };
  
  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };
  
  const handleDeclaration = () => {
    if (declaration) {
      declarationMutation.mutate(declaration);
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
        <p className="text-gray-500">Filing not found</p>
      </div>
    );
  }
  
  const filingData = filing.data;
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/filings')}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          <ArrowLeftIcon className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {filingData.filing_type} - {filingData.month}/{filingData.year}
          </h1>
          <p className="text-gray-600">
            Status: <span className="font-medium">{filingData.status}</span>
          </p>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Filing Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Filing Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Financial Year</p>
                <p className="font-medium">{filingData.financial_year}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Month</p>
                <p className="font-medium">{filingData.month}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Nil Filing</p>
                <p className="font-medium">{filingData.nil_filing ? 'Yes' : 'No'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Taxable Value</p>
                <p className="font-medium">₹{filingData.total_taxable_value?.toLocaleString() || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Tax</p>
                <p className="font-medium">₹{filingData.total_tax?.toLocaleString() || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Created At</p>
                <p className="font-medium">
                  {new Date(filingData.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
          
          {/* Upload Section */}
          {!filingData.nil_filing && filingData.status === 'draft' && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Invoices</h2>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <DocumentArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">Upload Excel file with invoice data</p>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileChange}
                  className="mb-4"
                />
                {selectedFile && (
                  <p className="text-sm text-gray-600 mb-4">
                    Selected: {selectedFile.name}
                  </p>
                )}
                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || uploadMutation.isPending}
                  className="btn-primary"
                >
                  {uploadMutation.isPending ? 'Uploading...' : 'Upload Invoices'}
                </button>
              </div>
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Card */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Status</h2>
            <div className={`p-4 rounded-lg ${
              filingData.status === 'filed' ? 'bg-green-50' :
              filingData.status === 'pending' ? 'bg-yellow-50' : 'bg-gray-50'
            }`}>
              <div className="flex items-center">
                <CheckCircleIcon className={`w-6 h-6 ${
                  filingData.status === 'filed' ? 'text-green-600' :
                  filingData.status === 'pending' ? 'text-yellow-600' : 'text-gray-600'
                }`} />
                <span className="ml-2 font-medium capitalize">{filingData.status}</span>
              </div>
            </div>
          </div>
          
          {/* Actions */}
          {filingData.status === 'draft' && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
              <button
                onClick={() => setShowDeclaration(true)}
                className="btn-primary w-full"
              >
                Submit Declaration
              </button>
            </div>
          )}
          
          {/* Filing Lock Info */}
          {filingData.filing_locked && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Lock Status</h2>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-700 font-medium">Filing is Locked</p>
                <p className="text-sm text-red-600 mt-1">{filingData.lock_reason}</p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Declaration Modal */}
      {showDeclaration && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Submit Declaration</h2>
            <p className="text-gray-600 mb-4">
              By submitting this declaration, you confirm that all the information provided 
              in the GST filing is accurate and complete.
            </p>
            <textarea
              value={declaration}
              onChange={(e) => setDeclaration(e.target.value)}
              placeholder="I declare that..."
              className="input-field h-32 mb-4"
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeclaration(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleDeclaration}
                disabled={!declaration || declarationMutation.isPending}
                className="btn-primary"
              >
                {declarationMutation.isPending ? 'Submitting...' : 'Submit Declaration'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilingDetailPage;
