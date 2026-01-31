/**
 * Franchise Management Page (Admin/Franchise Owner)
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    BuildingStorefrontIcon,
    UserGroupIcon,
    CurrencyRupeeIcon,
    MapPinIcon,
    ChartBarIcon,
    CheckCircleIcon,
    ClockIcon,
    PlusIcon,
    MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

// Mock data
const mockFranchises = [
    {
        id: '1',
        name: 'Chennai Central',
        owner_name: 'Rajesh Kumar',
        region: 'Tamil Nadu',
        pincodes: ['600001', '600002', '600003'],
        status: 'active',
        customers: 45,
        monthly_revenue: 125000,
        commission_rate: 15,
        created_at: '2024-01-01',
    },
    {
        id: '2',
        name: 'Mumbai West',
        owner_name: 'Priya Shah',
        region: 'Maharashtra',
        pincodes: ['400001', '400002'],
        status: 'active',
        customers: 62,
        monthly_revenue: 185000,
        commission_rate: 15,
        created_at: '2023-11-15',
    },
    {
        id: '3',
        name: 'Delhi North',
        owner_name: 'Amit Sharma',
        region: 'Delhi NCR',
        pincodes: ['110001'],
        status: 'pending',
        customers: 0,
        monthly_revenue: 0,
        commission_rate: 15,
        created_at: '2024-01-25',
    },
];

const FranchiseManagementPage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [showNewModal, setShowNewModal] = useState(false);

    const { data: franchises, isLoading } = useQuery({
        queryKey: ['franchises'],
        queryFn: async () => ({ data: mockFranchises }),
    });

    const franchiseList = franchises?.data || [];

    const filteredFranchises = franchiseList.filter((f: any) => {
        const matchesSearch = f.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            f.owner_name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'all' || f.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const totalRevenue = franchiseList.reduce((s: number, f: any) => s + (f.monthly_revenue || 0), 0);
    const totalCustomers = franchiseList.reduce((s: number, f: any) => s + (f.customers || 0), 0);
    const activeFranchises = franchiseList.filter((f: any) => f.status === 'active').length;

    const getStatusBadge = (status: string) => {
        const classes: Record<string, string> = {
            active: 'bg-green-100 text-green-700',
            pending: 'bg-yellow-100 text-yellow-700',
            suspended: 'bg-red-100 text-red-700',
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
                    <h1 className="text-2xl font-bold text-gray-900">Franchise Management</h1>
                    <p className="text-gray-600 mt-1">Manage your franchise network</p>
                </div>
                <button
                    onClick={() => setShowNewModal(true)}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusIcon className="w-5 h-5" />
                    Add Franchise
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-blue-100 text-sm">Total Franchises</p>
                            <p className="text-2xl font-bold">{franchiseList.length}</p>
                        </div>
                        <BuildingStorefrontIcon className="w-10 h-10 text-blue-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-green-500 to-emerald-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-green-100 text-sm">Active</p>
                            <p className="text-2xl font-bold">{activeFranchises}</p>
                        </div>
                        <CheckCircleIcon className="w-10 h-10 text-green-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-purple-500 to-violet-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-purple-100 text-sm">Total Customers</p>
                            <p className="text-2xl font-bold">{totalCustomers}</p>
                        </div>
                        <UserGroupIcon className="w-10 h-10 text-purple-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-orange-500 to-amber-500 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-orange-100 text-sm">Monthly Revenue</p>
                            <p className="text-2xl font-bold">₹{(totalRevenue / 100000).toFixed(1)}L</p>
                        </div>
                        <CurrencyRupeeIcon className="w-10 h-10 text-orange-200" />
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="card flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                    <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="text"
                        placeholder="Search franchises..."
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
                    <option value="active">Active</option>
                    <option value="pending">Pending</option>
                    <option value="suspended">Suspended</option>
                </select>
            </div>

            {/* Franchises Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredFranchises.map((franchise: any) => (
                    <div key={franchise.id} className="card hover:shadow-lg transition-shadow">
                        <div className="flex items-start justify-between mb-4">
                            <div>
                                <h3 className="font-bold text-lg text-gray-900">{franchise.name}</h3>
                                <p className="text-sm text-gray-500">{franchise.owner_name}</p>
                            </div>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(franchise.status)}`}>
                                {franchise.status}
                            </span>
                        </div>

                        <div className="space-y-3">
                            <div className="flex items-center text-sm text-gray-600">
                                <MapPinIcon className="w-4 h-4 mr-2" />
                                {franchise.region} ({franchise.pincodes.length} pincodes)
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                                <UserGroupIcon className="w-4 h-4 mr-2" />
                                {franchise.customers} customers
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                                <CurrencyRupeeIcon className="w-4 h-4 mr-2" />
                                ₹{(franchise.monthly_revenue / 1000).toFixed(0)}K / month
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t flex justify-between">
                            <span className="text-xs text-gray-400">
                                Since {new Date(franchise.created_at).toLocaleDateString()}
                            </span>
                            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                                View Details
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* New Franchise Modal */}
            {showNewModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 m-4 max-h-[90vh] overflow-y-auto">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Add New Franchise</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Franchise Name</label>
                                <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="e.g., Chennai Central" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Owner Name</label>
                                    <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                    <input type="email" className="w-full border border-gray-300 rounded-lg px-3 py-2" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                                <input type="tel" className="w-full border border-gray-300 rounded-lg px-3 py-2" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Region</label>
                                <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="e.g., Tamil Nadu" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Pincodes (comma separated)</label>
                                <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="600001, 600002, 600003" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Commission Rate (%)</label>
                                <input type="number" className="w-full border border-gray-300 rounded-lg px-3 py-2" defaultValue={15} />
                            </div>
                        </div>
                        <div className="flex gap-3 mt-6">
                            <button onClick={() => setShowNewModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg">
                                Cancel
                            </button>
                            <button className="flex-1 btn-primary">Add Franchise</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FranchiseManagementPage;
