/**
 * Support Tickets Page
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    TicketIcon,
    PlusIcon,
    ChatBubbleLeftRightIcon,
    ClockIcon,
    CheckCircleIcon,
    ExclamationCircleIcon,
    MagnifyingGlassIcon,
    PaperAirplaneIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

// Mock data
const mockTickets = [
    {
        id: '1',
        ticket_number: 'TKT-001',
        subject: 'GST Filing Issue',
        category: 'technical',
        priority: 'high',
        status: 'open',
        created_at: '2024-01-20T10:30:00',
        last_reply: '2024-01-21T14:00:00',
    },
    {
        id: '2',
        ticket_number: 'TKT-002',
        subject: 'Payment not reflecting',
        category: 'billing',
        priority: 'medium',
        status: 'in_progress',
        created_at: '2024-01-19T09:00:00',
        last_reply: '2024-01-20T11:00:00',
    },
    {
        id: '3',
        ticket_number: 'TKT-003',
        subject: 'ITR form clarification',
        category: 'service',
        priority: 'low',
        status: 'resolved',
        created_at: '2024-01-15T08:00:00',
        last_reply: '2024-01-18T16:00:00',
    },
];

const CATEGORIES = ['billing', 'technical', 'service', 'complaint', 'feedback', 'other'];
const PRIORITIES = ['low', 'medium', 'high', 'urgent'];

const SupportPage: React.FC = () => {
    const [showNewModal, setShowNewModal] = useState(false);
    const [selectedTicket, setSelectedTicket] = useState<any>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');

    const { data: tickets, isLoading } = useQuery({
        queryKey: ['support-tickets'],
        queryFn: async () => ({ data: mockTickets }),
    });

    const ticketList = tickets?.data || [];

    const filteredTickets = ticketList.filter((t: any) => {
        const matchesSearch = t.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
            t.ticket_number.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'all' || t.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const getStatusBadge = (status: string) => {
        const classes: Record<string, string> = {
            open: 'bg-blue-100 text-blue-700',
            in_progress: 'bg-yellow-100 text-yellow-700',
            waiting_customer: 'bg-orange-100 text-orange-700',
            resolved: 'bg-green-100 text-green-700',
            closed: 'bg-gray-100 text-gray-700',
        };
        return classes[status] || 'bg-gray-100 text-gray-700';
    };

    const getPriorityBadge = (priority: string) => {
        const classes: Record<string, string> = {
            low: 'bg-gray-100 text-gray-600',
            medium: 'bg-blue-100 text-blue-600',
            high: 'bg-orange-100 text-orange-600',
            urgent: 'bg-red-100 text-red-600',
        };
        return classes[priority] || 'bg-gray-100 text-gray-600';
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
                    <h1 className="text-2xl font-bold text-gray-900">Support</h1>
                    <p className="text-gray-600 mt-1">Get help with your queries and issues</p>
                </div>
                <button
                    onClick={() => setShowNewModal(true)}
                    className="btn-primary flex items-center gap-2"
                >
                    <PlusIcon className="w-5 h-5" />
                    New Ticket
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-blue-100 text-sm">Open</p>
                            <p className="text-2xl font-bold">{ticketList.filter((t: any) => t.status === 'open').length}</p>
                        </div>
                        <TicketIcon className="w-10 h-10 text-blue-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-yellow-500 to-orange-500 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-yellow-100 text-sm">In Progress</p>
                            <p className="text-2xl font-bold">{ticketList.filter((t: any) => t.status === 'in_progress').length}</p>
                        </div>
                        <ClockIcon className="w-10 h-10 text-yellow-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-green-500 to-emerald-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-green-100 text-sm">Resolved</p>
                            <p className="text-2xl font-bold">{ticketList.filter((t: any) => t.status === 'resolved').length}</p>
                        </div>
                        <CheckCircleIcon className="w-10 h-10 text-green-200" />
                    </div>
                </div>
                <div className="card bg-gradient-to-br from-purple-500 to-violet-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-purple-100 text-sm">Total</p>
                            <p className="text-2xl font-bold">{ticketList.length}</p>
                        </div>
                        <ChatBubbleLeftRightIcon className="w-10 h-10 text-purple-200" />
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="card flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                    <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="text"
                        placeholder="Search tickets..."
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
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                </select>
            </div>

            {/* Tickets List */}
            <div className="space-y-4">
                {filteredTickets.length > 0 ? (
                    filteredTickets.map((ticket: any) => (
                        <div
                            key={ticket.id}
                            className="card hover:shadow-lg transition-shadow cursor-pointer"
                            onClick={() => setSelectedTicket(ticket)}
                        >
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className="text-sm font-mono text-gray-500">{ticket.ticket_number}</span>
                                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getStatusBadge(ticket.status)}`}>
                                            {ticket.status.replace(/_/g, ' ')}
                                        </span>
                                        <span className={`px-2 py-0.5 text-xs font-medium rounded ${getPriorityBadge(ticket.priority)}`}>
                                            {ticket.priority}
                                        </span>
                                    </div>
                                    <h3 className="font-semibold text-gray-900">{ticket.subject}</h3>
                                    <p className="text-sm text-gray-500 mt-1">
                                        Created {new Date(ticket.created_at).toLocaleDateString()} •
                                        Last reply {new Date(ticket.last_reply).toLocaleDateString()}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                                        {ticket.category}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="card text-center py-12">
                        <TicketIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-500">No tickets found</p>
                        <button
                            onClick={() => setShowNewModal(true)}
                            className="text-primary-600 hover:text-primary-700 text-sm mt-2"
                        >
                            Create your first ticket
                        </button>
                    </div>
                )}
            </div>

            {/* New Ticket Modal */}
            {showNewModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 m-4">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Create Support Ticket</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                                <input type="text" className="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="Brief description of your issue" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                                    <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                        {CATEGORIES.map(cat => (
                                            <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                                    <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                                        {PRIORITIES.map(p => (
                                            <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                <textarea rows={4} className="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="Describe your issue in detail..."></textarea>
                            </div>
                        </div>
                        <div className="flex gap-3 mt-6">
                            <button onClick={() => setShowNewModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg">
                                Cancel
                            </button>
                            <button className="flex-1 btn-primary flex items-center justify-center gap-2">
                                <PaperAirplaneIcon className="w-4 h-4" />
                                Submit Ticket
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Ticket Detail Modal */}
            {selectedTicket && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl p-6 m-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex items-start justify-between mb-4">
                            <div>
                                <p className="text-sm font-mono text-gray-500">{selectedTicket.ticket_number}</p>
                                <h2 className="text-xl font-bold text-gray-900">{selectedTicket.subject}</h2>
                            </div>
                            <button onClick={() => setSelectedTicket(null)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <div className="flex gap-2 mb-4">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(selectedTicket.status)}`}>
                                {selectedTicket.status.replace(/_/g, ' ')}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityBadge(selectedTicket.priority)}`}>
                                {selectedTicket.priority}
                            </span>
                        </div>

                        {/* Conversation */}
                        <div className="border rounded-lg p-4 mb-4 bg-gray-50 min-h-[200px]">
                            <p className="text-gray-500 text-center">Conversation history will appear here</p>
                        </div>

                        {/* Reply */}
                        <div className="flex gap-3">
                            <input type="text" className="flex-1 border border-gray-300 rounded-lg px-3 py-2" placeholder="Type your reply..." />
                            <button className="btn-primary flex items-center gap-2">
                                <PaperAirplaneIcon className="w-4 h-4" />
                                Send
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SupportPage;
