/**
 * Business Services Page - Company, FSSAI, MSME, PAN/TAN
 */
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
    BuildingOffice2Icon,
    ShieldCheckIcon,
    BuildingStorefrontIcon,
    IdentificationIcon,
    PlusIcon,
    ClockIcon,
    CheckCircleIcon,
    DocumentTextIcon,
    ArrowRightIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

const SERVICES = [
    {
        id: 'company',
        name: 'Company Incorporation',
        description: 'Register Pvt Ltd, LLP, OPC, or Section 8 Company',
        icon: BuildingOffice2Icon,
        color: 'from-blue-500 to-indigo-600',
        types: ['private_limited', 'llp', 'opc', 'section_8'],
    },
    {
        id: 'fssai',
        name: 'FSSAI Registration',
        description: 'Food license - Basic, State, or Central',
        icon: ShieldCheckIcon,
        color: 'from-green-500 to-emerald-600',
        types: ['basic', 'state', 'central'],
    },
    {
        id: 'msme',
        name: 'MSME/Udyam Registration',
        description: 'Register as Micro, Small, or Medium Enterprise',
        icon: BuildingStorefrontIcon,
        color: 'from-orange-500 to-amber-600',
        types: ['micro', 'small', 'medium'],
    },
    {
        id: 'pantan',
        name: 'PAN/TAN Services',
        description: 'New PAN/TAN or Corrections',
        icon: IdentificationIcon,
        color: 'from-purple-500 to-violet-600',
        types: ['pan_new', 'pan_correction', 'tan_new', 'tan_correction'],
    },
];

// Mock applications
const mockApplications = [
    {
        id: '1',
        service_type: 'company_incorporation',
        company_type: 'private_limited',
        status: 'processing',
        created_at: '2024-01-15',
        applicant_name: 'Tech Ventures Pvt Ltd',
    },
    {
        id: '2',
        service_type: 'fssai_registration',
        license_type: 'state',
        status: 'completed',
        created_at: '2024-01-10',
        applicant_name: 'Food Corp',
    },
    {
        id: '3',
        service_type: 'msme_registration',
        enterprise_type: 'micro',
        status: 'pending_documents',
        created_at: '2024-01-08',
        applicant_name: 'Small Business LLC',
    },
];

const BusinessServicesPage: React.FC = () => {
    const [selectedService, setSelectedService] = useState<string | null>(null);
    const [showNewModal, setShowNewModal] = useState(false);

    const { data: applications, isLoading } = useQuery({
        queryKey: ['business-applications'],
        queryFn: async () => ({ data: mockApplications }),
    });

    const appList = applications?.data || [];

    const getStatusBadge = (status: string) => {
        const classes: Record<string, { bg: string; text: string }> = {
            draft: { bg: 'bg-gray-100', text: 'text-gray-700' },
            submitted: { bg: 'bg-blue-100', text: 'text-blue-700' },
            pending_documents: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
            processing: { bg: 'bg-indigo-100', text: 'text-indigo-700' },
            completed: { bg: 'bg-green-100', text: 'text-green-700' },
            rejected: { bg: 'bg-red-100', text: 'text-red-700' },
        };
        const style = classes[status] || classes.draft;
        return `${style.bg} ${style.text}`;
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
                    <h1 className="text-2xl font-bold text-gray-900">Business Services</h1>
                    <p className="text-gray-600 mt-1">Register your business with government authorities</p>
                </div>
            </div>

            {/* Service Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {SERVICES.map((service) => {
                    const Icon = service.icon;
                    return (
                        <div
                            key={service.id}
                            className={`card cursor-pointer hover:shadow-lg transition-all duration-300 bg-gradient-to-br ${service.color} text-white`}
                            onClick={() => {
                                setSelectedService(service.id);
                                setShowNewModal(true);
                            }}
                        >
                            <div className="flex flex-col h-full">
                                <Icon className="w-10 h-10 mb-4 opacity-90" />
                                <h3 className="font-bold text-lg mb-2">{service.name}</h3>
                                <p className="text-sm opacity-80 flex-1">{service.description}</p>
                                <div className="flex items-center mt-4 text-sm font-medium">
                                    Get Started <ArrowRightIcon className="w-4 h-4 ml-2" />
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Total Applications</p>
                            <p className="text-2xl font-bold text-gray-900">{appList.length}</p>
                        </div>
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <DocumentTextIcon className="w-6 h-6 text-blue-600" />
                        </div>
                    </div>
                </div>
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">In Progress</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {appList.filter((a: any) => !['completed', 'rejected'].includes(a.status)).length}
                            </p>
                        </div>
                        <div className="p-3 bg-yellow-100 rounded-lg">
                            <ClockIcon className="w-6 h-6 text-yellow-600" />
                        </div>
                    </div>
                </div>
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Completed</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {appList.filter((a: any) => a.status === 'completed').length}
                            </p>
                        </div>
                        <div className="p-3 bg-green-100 rounded-lg">
                            <CheckCircleIcon className="w-6 h-6 text-green-600" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Applications List */}
            <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Applications</h2>
                {appList.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Applicant</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {appList.map((app: any) => (
                                    <tr key={app.id} className="hover:bg-gray-50">
                                        <td className="px-4 py-4">
                                            <span className="font-medium text-gray-900">
                                                {app.service_type.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4 text-gray-600">{app.applicant_name}</td>
                                        <td className="px-4 py-4 text-gray-600">{new Date(app.created_at).toLocaleDateString()}</td>
                                        <td className="px-4 py-4">
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(app.status)}`}>
                                                {app.status.replace(/_/g, ' ')}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4">
                                            <Link to={`/services/${app.id}`} className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                                                View Details
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <DocumentTextIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-500">No applications yet</p>
                        <p className="text-sm text-gray-400 mt-1">Choose a service above to get started</p>
                    </div>
                )}
            </div>

            {/* New Application Modal */}
            {showNewModal && selectedService && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 m-4 max-h-[90vh] overflow-y-auto">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">
                            New {SERVICES.find(s => s.id === selectedService)?.name}
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name / Business Name</label>
                                <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="Enter name" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                <input type="email" className="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="Enter email" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                                <input type="tel" className="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="Enter phone" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                                <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                    {SERVICES.find(s => s.id === selectedService)?.types.map(t => (
                                        <option key={t} value={t}>{t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                        <div className="flex gap-3 mt-6">
                            <button onClick={() => setShowNewModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg">
                                Cancel
                            </button>
                            <button className="flex-1 btn-primary">Submit Application</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BusinessServicesPage;
