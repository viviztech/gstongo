/**
 * Analytics Dashboard Page
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    ChartBarIcon,
    ArrowTrendingUpIcon,
    ArrowTrendingDownIcon,
    CurrencyRupeeIcon,
    DocumentTextIcon,
    UserGroupIcon,
    ClockIcon,
    CalendarDaysIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/Common/LoadingSpinner';

// Mock data for charts/analytics
const mockAnalytics = {
    summary: {
        total_revenue: 1250000,
        revenue_change: 12.5,
        total_filings: 156,
        filings_change: 8.2,
        total_customers: 89,
        customers_change: 15.3,
        avg_processing_time: 2.4,
        time_change: -18.5,
    },
    monthly_revenue: [
        { month: 'Aug', revenue: 85000 },
        { month: 'Sep', revenue: 92000 },
        { month: 'Oct', revenue: 110000 },
        { month: 'Nov', revenue: 125000 },
        { month: 'Dec', revenue: 145000 },
        { month: 'Jan', revenue: 168000 },
    ],
    filing_breakdown: [
        { type: 'GSTR-1', count: 45, percentage: 29 },
        { type: 'GSTR-3B', count: 52, percentage: 33 },
        { type: 'ITR', count: 28, percentage: 18 },
        { type: 'TDS', count: 18, percentage: 12 },
        { type: 'Others', count: 13, percentage: 8 },
    ],
    recent_activity: [
        { id: '1', action: 'GSTR-1 Filed', customer: 'ABC Corp', time: '2 hours ago' },
        { id: '2', action: 'Payment Received', customer: 'XYZ Ltd', time: '4 hours ago' },
        { id: '3', action: 'ITR Submitted', customer: 'John Doe', time: '6 hours ago' },
        { id: '4', action: 'New Registration', customer: 'Tech Startup', time: '8 hours ago' },
    ],
};

const AnalyticsPage: React.FC = () => {
    const [dateRange, setDateRange] = useState('30d');

    const { data: analytics, isLoading } = useQuery({
        queryKey: ['analytics', dateRange],
        queryFn: async () => ({ data: mockAnalytics }),
    });

    const data = analytics?.data || mockAnalytics;

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
                    <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
                    <p className="text-gray-600 mt-1">Business insights and performance metrics</p>
                </div>
                <div className="flex items-center gap-2">
                    <CalendarDaysIcon className="w-5 h-5 text-gray-400" />
                    <select
                        value={dateRange}
                        onChange={(e) => setDateRange(e.target.value)}
                        className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500"
                    >
                        <option value="7d">Last 7 days</option>
                        <option value="30d">Last 30 days</option>
                        <option value="90d">Last 90 days</option>
                        <option value="1y">Last year</option>
                    </select>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Total Revenue</p>
                            <p className="text-2xl font-bold text-gray-900">₹{(data.summary.total_revenue / 100000).toFixed(1)}L</p>
                            <div className={`flex items-center mt-1 text-sm ${data.summary.revenue_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {data.summary.revenue_change >= 0 ? <ArrowTrendingUpIcon className="w-4 h-4 mr-1" /> : <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />}
                                {Math.abs(data.summary.revenue_change)}% vs last period
                            </div>
                        </div>
                        <div className="p-3 bg-green-100 rounded-lg">
                            <CurrencyRupeeIcon className="w-6 h-6 text-green-600" />
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Total Filings</p>
                            <p className="text-2xl font-bold text-gray-900">{data.summary.total_filings}</p>
                            <div className={`flex items-center mt-1 text-sm ${data.summary.filings_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {data.summary.filings_change >= 0 ? <ArrowTrendingUpIcon className="w-4 h-4 mr-1" /> : <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />}
                                {Math.abs(data.summary.filings_change)}% vs last period
                            </div>
                        </div>
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <DocumentTextIcon className="w-6 h-6 text-blue-600" />
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Active Customers</p>
                            <p className="text-2xl font-bold text-gray-900">{data.summary.total_customers}</p>
                            <div className={`flex items-center mt-1 text-sm ${data.summary.customers_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {data.summary.customers_change >= 0 ? <ArrowTrendingUpIcon className="w-4 h-4 mr-1" /> : <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />}
                                {Math.abs(data.summary.customers_change)}% vs last period
                            </div>
                        </div>
                        <div className="p-3 bg-purple-100 rounded-lg">
                            <UserGroupIcon className="w-6 h-6 text-purple-600" />
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Avg Processing Time</p>
                            <p className="text-2xl font-bold text-gray-900">{data.summary.avg_processing_time} days</p>
                            <div className={`flex items-center mt-1 text-sm ${data.summary.time_change <= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {data.summary.time_change <= 0 ? <ArrowTrendingDownIcon className="w-4 h-4 mr-1" /> : <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />}
                                {Math.abs(data.summary.time_change)}% vs last period
                            </div>
                        </div>
                        <div className="p-3 bg-orange-100 rounded-lg">
                            <ClockIcon className="w-6 h-6 text-orange-600" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Revenue Chart */}
                <div className="card">
                    <h3 className="font-semibold text-gray-900 mb-4">Revenue Trend</h3>
                    <div className="h-64 flex items-end justify-between gap-2">
                        {data.monthly_revenue.map((item: any, index: number) => {
                            const maxRevenue = Math.max(...data.monthly_revenue.map((r: any) => r.revenue));
                            const height = (item.revenue / maxRevenue) * 100;
                            return (
                                <div key={index} className="flex-1 flex flex-col items-center">
                                    <div
                                        className="w-full bg-gradient-to-t from-primary-500 to-primary-400 rounded-t-lg transition-all hover:from-primary-600 hover:to-primary-500"
                                        style={{ height: `${height}%` }}
                                    ></div>
                                    <p className="text-xs text-gray-500 mt-2">{item.month}</p>
                                    <p className="text-xs font-medium text-gray-700">₹{(item.revenue / 1000).toFixed(0)}K</p>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Filing Breakdown */}
                <div className="card">
                    <h3 className="font-semibold text-gray-900 mb-4">Filing Breakdown</h3>
                    <div className="space-y-4">
                        {data.filing_breakdown.map((item: any, index: number) => {
                            const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-gray-500'];
                            return (
                                <div key={index}>
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-sm font-medium text-gray-700">{item.type}</span>
                                        <span className="text-sm text-gray-500">{item.count} ({item.percentage}%)</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className={`${colors[index]} h-2 rounded-full transition-all`}
                                            style={{ width: `${item.percentage}%` }}
                                        ></div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
                <h3 className="font-semibold text-gray-900 mb-4">Recent Activity</h3>
                <div className="space-y-4">
                    {data.recent_activity.map((activity: any) => (
                        <div key={activity.id} className="flex items-center justify-between py-3 border-b last:border-0">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                                    <ChartBarIcon className="w-5 h-5 text-primary-600" />
                                </div>
                                <div>
                                    <p className="font-medium text-gray-900">{activity.action}</p>
                                    <p className="text-sm text-gray-500">{activity.customer}</p>
                                </div>
                            </div>
                            <span className="text-sm text-gray-400">{activity.time}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Quick Reports */}
            <div className="card">
                <h3 className="font-semibold text-gray-900 mb-4">Quick Reports</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {['Revenue Report', 'Filing Summary', 'Customer Report', 'Performance Report'].map((report, index) => (
                        <button
                            key={index}
                            className="p-4 border-2 border-dashed border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-center"
                        >
                            <DocumentTextIcon className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                            <p className="font-medium text-gray-700">{report}</p>
                            <p className="text-xs text-gray-500 mt-1">Download PDF</p>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPage;
