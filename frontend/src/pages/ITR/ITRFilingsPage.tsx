/**
 * ITR Filing List Page
 */
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
    DocumentTextIcon,
    PlusIcon,
    FunnelIcon,
    MagnifyingGlassIcon,
    CalendarDaysIcon,
    CurrencyRupeeIcon,
    CheckCircleIcon,
    ClockIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

// Mock data for demonstration
const mockITRFilings = [
    {
        id: '1',
        assessment_year: '2024-25',
        filing_type: 'ITR-1',
        status: 'draft',
        total_income: 850000,
        tax_payable: 25000,
        created_at: '2024-01-15',
    },
    {
        id: '2',
        assessment_year: '2023-24',
        filing_type: 'ITR-1',
        status: 'filed',
        total_income: 780000,
        tax_payable: 18000,
        acknowledgment_number: 'ACK123456789',
        created_at: '2023-07-20',
    },
];

const ITR_TYPES = ['ITR-1', 'ITR-2', 'ITR-3', 'ITR-4'];
const STATUS_OPTIONS = ['all', 'draft', 'pending', 'filed', 'verified'];

const ITRFilingsPage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [showNewModal, setShowNewModal] = useState(false);

    // In production, this would call the actual API
    const { data: filings, isLoading } = useQuery({
        queryKey: ['itr-filings'],
        queryFn: async () => {
            // Simulating API call
            return { data: mockITRFilings };
        },
    });

    const filingList = filings?.data || [];

    const filteredFilings = filingList.filter((filing: any) => {
        const matchesSearch = filing.assessment_year?.includes(searchTerm) ||
            filing.filing_type?.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'all' || filing.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const getStatusBadge = (status: string) => {
        const statusClasses: Record<string, string> = {
            draft: 'bg-gray-100 text-gray-700',
            pending: 'bg-yellow-100 text-yellow-700',
            verified: 'bg-blue-100 text-blue-700',
            filed: 'bg-green-100 text-green-700',
        };
        return statusClasses[status] || 'bg-gray-100 text-gray-700';
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
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Income Tax Returns</h1>
                    <p className="text-gray-600 mt-1">Manage your ITR filings</p>
                </div>
                <button
                    onClick={() => setShowNewModal(true)}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusIcon className="w-5 h-5" />
                    New ITR Filing
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-blue-100 text-sm">Total Filings</p>
                            <p className="text-2xl font-bold">{filingList.length}</p>
                        </div>
                        <DocumentTextIcon className="w-10 h-10 text-blue-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-yellow-500 to-orange-500 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-yellow-100 text-sm">Pending</p>
                            <p className="text-2xl font-bold">
                                {filingList.filter((f: any) => f.status === 'pending').length}
                            </p>
                        </div>
                        <ClockIcon className="w-10 h-10 text-yellow-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-green-500 to-emerald-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-green-100 text-sm">Filed</p>
                            <p className="text-2xl font-bold">
                                {filingList.filter((f: any) => f.status === 'filed').length}
                            </p>
                        </div>
                        <CheckCircleIcon className="w-10 h-10 text-green-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-purple-500 to-indigo-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-purple-100 text-sm">Total Tax Paid</p>
                            <p className="text-2xl font-bold">
                                ₹{filingList.reduce((sum: number, f: any) => sum + (f.tax_payable || 0), 0).toLocaleString()}
                            </p>
                        </div>
                        <CurrencyRupeeIcon className="w-10 h-10 text-purple-200" />
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
                            placeholder="Search by year or type..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <FunnelIcon className="w-5 h-5 text-gray-400" />
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500"
                        >
                            {STATUS_OPTIONS.map(status => (
                                <option key={status} value={status}>
                                    {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* Filings List */}
            <div className="card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assessment Year</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Income</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tax Payable</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {filteredFilings.length > 0 ? (
                                filteredFilings.map((filing: any) => (
                                    <tr key={filing.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <CalendarDaysIcon className="w-5 h-5 text-gray-400 mr-2" />
                                                <span className="font-medium text-gray-900">{filing.assessment_year}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                                                {filing.filing_type}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                                            ₹{(filing.total_income || 0).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                                            ₹{(filing.tax_payable || 0).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(filing.status)}`}>
                                                {filing.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <Link
                                                to={`/itr/${filing.id}`}
                                                className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                                            >
                                                View Details
                                            </Link>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center">
                                        <DocumentTextIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                                        <p className="text-gray-500">No ITR filings found</p>
                                        <button
                                            onClick={() => setShowNewModal(true)}
                                            className="text-primary-600 hover:text-primary-700 text-sm mt-2"
                                        >
                                            Create your first ITR filing
                                        </button>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* New Filing Modal */}
            {showNewModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 m-4">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Start New ITR Filing</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Assessment Year</label>
                                <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                    <option>2024-25</option>
                                    <option>2023-24</option>
                                    <option>2022-23</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">ITR Type</label>
                                <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                    {ITR_TYPES.map(type => (
                                        <option key={type} value={type}>{type}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => setShowNewModal(false)}
                                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                            <button className="flex-1 btn-primary">
                                Start Filing
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ITRFilingsPage;
