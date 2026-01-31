/**
 * Document Vault Page - Secure document management
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    FolderIcon,
    DocumentIcon,
    CloudArrowUpIcon,
    MagnifyingGlassIcon,
    ShareIcon,
    TrashIcon,
    EyeIcon,
    ArrowDownTrayIcon,
    PlusIcon,
    FolderPlusIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

// Mock data
const mockCategories = [
    { id: '1', name: 'GST Documents', document_count: 12, icon: '📊' },
    { id: '2', name: 'ITR Documents', document_count: 8, icon: '📄' },
    { id: '3', name: 'Business Registrations', document_count: 5, icon: '🏢' },
    { id: '4', name: 'Contracts', document_count: 15, icon: '📜' },
    { id: '5', name: 'Invoices', document_count: 45, icon: '🧾' },
];

const mockDocuments = [
    { id: '1', name: 'GSTR-1_Jan2024.pdf', category: 'GST Documents', size: '256 KB', uploaded_at: '2024-01-15', file_type: 'pdf' },
    { id: '2', name: 'ITR_AY2024.pdf', category: 'ITR Documents', size: '1.2 MB', uploaded_at: '2024-01-10', file_type: 'pdf' },
    { id: '3', name: 'Company_Registration.pdf', category: 'Business Registrations', size: '890 KB', uploaded_at: '2024-01-05', file_type: 'pdf' },
    { id: '4', name: 'Invoice_001.xlsx', category: 'Invoices', size: '45 KB', uploaded_at: '2024-01-20', file_type: 'excel' },
    { id: '5', name: 'Form16_2024.pdf', category: 'ITR Documents', size: '156 KB', uploaded_at: '2024-01-18', file_type: 'pdf' },
];

const DocumentVaultPage: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

    const { data: docData, isLoading } = useQuery({
        queryKey: ['documents'],
        queryFn: async () => ({ categories: mockCategories, documents: mockDocuments }),
    });

    const categories = docData?.categories || [];
    const documents = docData?.documents || [];

    const filteredDocs = documents.filter((doc: any) => {
        const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory = !selectedCategory || doc.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    const getFileIcon = (type: string) => {
        switch (type) {
            case 'pdf':
                return <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center text-red-600 font-bold text-xs">PDF</div>;
            case 'excel':
                return <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-bold text-xs">XLS</div>;
            case 'word':
                return <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold text-xs">DOC</div>;
            default:
                return <DocumentIcon className="w-10 h-10 text-gray-400" />;
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
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Document Vault</h1>
                    <p className="text-gray-600 mt-1">Secure storage for all your important documents</p>
                </div>
                <div className="flex gap-3">
                    <button className="px-4 py-2 border border-gray-300 rounded-lg flex items-center gap-2 hover:bg-gray-50">
                        <FolderPlusIcon className="w-5 h-5" />
                        New Folder
                    </button>
                    <button
                        onClick={() => setShowUploadModal(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <CloudArrowUpIcon className="w-5 h-5" />
                        Upload
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card bg-gradient-to-br from-violet-500 to-purple-600 text-white">
                    <p className="text-violet-100 text-sm">Total Documents</p>
                    <p className="text-2xl font-bold">{documents.length}</p>
                </div>
                <div className="card bg-gradient-to-br from-blue-500 to-cyan-600 text-white">
                    <p className="text-blue-100 text-sm">Categories</p>
                    <p className="text-2xl font-bold">{categories.length}</p>
                </div>
                <div className="card bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
                    <p className="text-emerald-100 text-sm">Storage Used</p>
                    <p className="text-2xl font-bold">2.8 GB</p>
                </div>
                <div className="card bg-gradient-to-br from-orange-500 to-red-500 text-white">
                    <p className="text-orange-100 text-sm">Shared</p>
                    <p className="text-2xl font-bold">5</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Categories Sidebar */}
                <div className="lg:col-span-1">
                    <div className="card">
                        <h3 className="font-semibold text-gray-900 mb-4">Categories</h3>
                        <div className="space-y-2">
                            <button
                                onClick={() => setSelectedCategory(null)}
                                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${!selectedCategory ? 'bg-primary-100 text-primary-700' : 'hover:bg-gray-100'
                                    }`}
                            >
                                <span className="flex items-center gap-2">
                                    <FolderIcon className="w-5 h-5" />
                                    All Documents
                                </span>
                                <span className="text-sm text-gray-500">{documents.length}</span>
                            </button>
                            {categories.map((cat: any) => (
                                <button
                                    key={cat.id}
                                    onClick={() => setSelectedCategory(cat.name)}
                                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${selectedCategory === cat.name ? 'bg-primary-100 text-primary-700' : 'hover:bg-gray-100'
                                        }`}
                                >
                                    <span className="flex items-center gap-2">
                                        <span>{cat.icon}</span>
                                        <span className="text-sm">{cat.name}</span>
                                    </span>
                                    <span className="text-sm text-gray-500">{cat.document_count}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Documents Grid */}
                <div className="lg:col-span-3">
                    {/* Search & View Toggle */}
                    <div className="card mb-4">
                        <div className="flex gap-4">
                            <div className="flex-1 relative">
                                <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                                <input
                                    type="text"
                                    placeholder="Search documents..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                            <div className="flex border border-gray-300 rounded-lg overflow-hidden">
                                <button
                                    onClick={() => setViewMode('grid')}
                                    className={`px-3 py-2 ${viewMode === 'grid' ? 'bg-primary-100 text-primary-700' : 'hover:bg-gray-100'}`}
                                >
                                    Grid
                                </button>
                                <button
                                    onClick={() => setViewMode('list')}
                                    className={`px-3 py-2 ${viewMode === 'list' ? 'bg-primary-100 text-primary-700' : 'hover:bg-gray-100'}`}
                                >
                                    List
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Documents */}
                    {viewMode === 'grid' ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            {filteredDocs.map((doc: any) => (
                                <div key={doc.id} className="card hover:shadow-lg transition-shadow group">
                                    <div className="flex items-start justify-between mb-4">
                                        {getFileIcon(doc.file_type)}
                                        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                                            <button className="p-1 hover:bg-gray-100 rounded">
                                                <EyeIcon className="w-4 h-4 text-gray-500" />
                                            </button>
                                            <button className="p-1 hover:bg-gray-100 rounded">
                                                <ArrowDownTrayIcon className="w-4 h-4 text-gray-500" />
                                            </button>
                                            <button className="p-1 hover:bg-gray-100 rounded">
                                                <ShareIcon className="w-4 h-4 text-gray-500" />
                                            </button>
                                        </div>
                                    </div>
                                    <h4 className="font-medium text-gray-900 truncate">{doc.name}</h4>
                                    <p className="text-sm text-gray-500 mt-1">{doc.size}</p>
                                    <p className="text-xs text-gray-400 mt-2">{new Date(doc.uploaded_at).toLocaleDateString()}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="card overflow-hidden">
                            <table className="w-full">
                                <thead className="bg-gray-50 border-b">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y">
                                    {filteredDocs.map((doc: any) => (
                                        <tr key={doc.id} className="hover:bg-gray-50">
                                            <td className="px-4 py-3 flex items-center gap-3">
                                                {getFileIcon(doc.file_type)}
                                                <span className="font-medium text-gray-900">{doc.name}</span>
                                            </td>
                                            <td className="px-4 py-3 text-gray-600">{doc.category}</td>
                                            <td className="px-4 py-3 text-gray-600">{doc.size}</td>
                                            <td className="px-4 py-3 text-gray-600">{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                                            <td className="px-4 py-3">
                                                <div className="flex gap-2">
                                                    <button className="p-1 hover:bg-gray-100 rounded"><EyeIcon className="w-4 h-4" /></button>
                                                    <button className="p-1 hover:bg-gray-100 rounded"><ArrowDownTrayIcon className="w-4 h-4" /></button>
                                                    <button className="p-1 hover:bg-gray-100 rounded"><ShareIcon className="w-4 h-4" /></button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {/* Upload Modal */}
            {showUploadModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 m-4">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Documents</h2>
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
                            <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600 mb-2">Drag & drop files here</p>
                            <p className="text-sm text-gray-400 mb-4">or</p>
                            <button className="btn-primary">Browse Files</button>
                        </div>
                        <div className="mt-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                            <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                {categories.map((cat: any) => (
                                    <option key={cat.id} value={cat.name}>{cat.name}</option>
                                ))}
                            </select>
                        </div>
                        <div className="flex gap-3 mt-6">
                            <button onClick={() => setShowUploadModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg">
                                Cancel
                            </button>
                            <button className="flex-1 btn-primary">Upload</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DocumentVaultPage;
