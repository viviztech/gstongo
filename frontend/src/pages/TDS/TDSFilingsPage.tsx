/**
 * TDS Filing List Page
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
    BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

// Mock data
const mockTDSReturns = [
    {
        id: '1',
        return_type: '24Q',
        financial_year: '2024-25',
        quarter: 'Q3',
        status: 'draft',
        tan_number: 'ABCD12345E',
        total_deducted: 125000,
        total_deposited: 125000,
        created_at: '2024-01-10',
    },
    {
        id: '2',
        return_type: '26Q',
        financial_year: '2024-25',
        quarter: 'Q2',
        status: 'filed',
        tan_number: 'ABCD12345E',
        total_deducted: 85000,
        total_deposited: 85000,
        acknowledgment_number: 'TDS123456',
        created_at: '2023-10-15',
    },
];

const RETURN_TYPES = [
    { value: '24Q', label: 'Form 24Q - Salary' },
    { value: '26Q', label: 'Form 26Q - Non-Salary' },
    { value: '27Q', label: 'Form 27Q - NRI Payments' },
    { value: '27EQ', label: 'Form 27EQ - TCS' },
];

const QUARTERS = ['Q1', 'Q2', 'Q3', 'Q4'];

const TDSFilingsPage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [showNewModal, setShowNewModal] = useState(false);

    const { data: returns, isLoading } = useQuery({
        queryKey: ['tds-returns'],
        queryFn: async () => ({ data: mockTDSReturns }),
    });

    const returnList = returns?.data || [];

    const filteredReturns = returnList.filter((ret: any) => {
        const matchesSearch = ret.return_type?.includes(searchTerm) ||
            ret.financial_year?.includes(searchTerm);
        const matchesStatus = statusFilter === 'all' || ret.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const getStatusBadge = (status: string) => {
        const classes: Record<string, string> = {
            draft: 'bg-gray-100 text-gray-700',
            pending: 'bg-yellow-100 text-yellow-700',
            verified: 'bg-blue-100 text-blue-700',
            filed: 'bg-green-100 text-green-700',
        };
        return classes[status] || 'bg-gray-100 text-gray-700';
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
                    <h1 className="text-2xl font-bold text-gray-900">TDS Returns</h1>
                    <p className="text-gray-600 mt-1">Manage your TDS filing and compliance</p>
                </div>
                <button
                    onClick={() => setShowNewModal(true)}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusIcon className="w-5 h-5" />
                    New TDS Return
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-indigo-100 text-sm">Total Returns</p>
                            <p className="text-2xl font-bold">{returnList.length}</p>
                        </div>
                        <DocumentTextIcon className="w-10 h-10 text-indigo-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-amber-500 to-orange-500 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-amber-100 text-sm">Pending</p>
                            <p className="text-2xl font-bold">
                                {returnList.filter((r: any) => r.status !== 'filed').length}
                            </p>
                        </div>
                        <ClockIcon className="w-10 h-10 text-amber-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-emerald-100 text-sm">Total Deducted</p>
                            <p className="text-2xl font-bold">
                                ₹{returnList.reduce((s: number, r: any) => s + (r.total_deducted || 0), 0).toLocaleString()}
                            </p>
                        </div>
                        <CurrencyRupeeIcon className="w-10 h-10 text-emerald-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-cyan-500 to-blue-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-cyan-100 text-sm">Total Deposited</p>
                            <p className="text-2xl font-bold">
                                ₹{returnList.reduce((s: number, r: any) => s + (r.total_deposited || 0), 0).toLocaleString()}
                            </p>
                        </div>
                        <CheckCircleIcon className="w-10 h-10 text-cyan-200" />
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="card flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                    <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="text"
                        placeholder="Search by type or year..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                </div>
                <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-2"
                >
                    <option value="all">All Status</option>
                    <option value="draft">Draft</option>
                    <option value="pending">Pending</option>
                    <option value="filed">Filed</option>
                </select>
            </div>

            {/* Returns Table */}
            <div className="card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Form Type</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">FY / Quarter</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">TAN</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deducted</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deposited</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {filteredReturns.map((ret: any) => (
                                <tr key={ret.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className="px-2 py-1 text-xs font-medium bg-indigo-100 text-indigo-700 rounded">
                                            {ret.return_type}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <CalendarDaysIcon className="w-4 h-4 text-gray-400 mr-2" />
                                            {ret.financial_year} - {ret.quarter}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap font-mono text-sm">
                                        {ret.tan_number}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        ₹{(ret.total_deducted || 0).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        ₹{(ret.total_deposited || 0).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(ret.status)}`}>
                                            {ret.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <Link to={`/tds/${ret.id}`} className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                                            View
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* New Return Modal */}
            {showNewModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 m-4">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">New TDS Return</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Return Type</label>
                                <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                    {RETURN_TYPES.map(type => (
                                        <option key={type.value} value={type.value}>{type.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Financial Year</label>
                                    <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                        <option>2024-25</option>
                                        <option>2023-24</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Quarter</label>
                                    <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                        {QUARTERS.map(q => (
                                            <option key={q} value={q}>{q}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">TAN Number</label>
                                <input type="text" placeholder="Enter TAN" className="w-full border border-gray-300 rounded-lg px-3 py-2" />
                            </div>
                        </div>
                        <div className="flex gap-3 mt-6">
                            <button onClick={() => setShowNewModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg">
                                Cancel
                            </button>
                            <button className="flex-1 btn-primary">Create Return</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TDSFilingsPage;
