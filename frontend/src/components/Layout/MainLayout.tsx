/**
 * Main Layout Component
 */
import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  HomeIcon,
  DocumentTextIcon,
  CurrencyRupeeIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  BellIcon,
  Bars3Icon,
  XMarkIcon,
  CalculatorIcon,
  BuildingOffice2Icon,
  FolderIcon,
  TicketIcon,
  ChartBarIcon,
  BanknotesIcon,
  BookOpenIcon,
  BuildingStorefrontIcon,
} from '@heroicons/react/24/outline';
import { useQuery } from '@tanstack/react-query';
import { userAPI } from '../../services/api';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  roles?: string[];
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'GST Filings', href: '/filings', icon: DocumentTextIcon },
  { name: 'ITR Filings', href: '/itr', icon: CalculatorIcon },
  { name: 'TDS Returns', href: '/tds', icon: BanknotesIcon },
  { name: 'Business Services', href: '/services', icon: BuildingOffice2Icon },
  { name: 'Document Vault', href: '/vault', icon: FolderIcon },
  { name: 'Invoices', href: '/invoices', icon: CurrencyRupeeIcon },
  { name: 'Support', href: '/support', icon: TicketIcon },
  { name: 'Help Center', href: '/help', icon: BookOpenIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Franchise', href: '/franchise', icon: BuildingStorefrontIcon, roles: ['admin', 'franchise_owner'] },
  { name: 'Profile', href: '/profile', icon: UserCircleIcon },
];

const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // In production, this would come from auth context
  const userRole = 'admin'; // Mock user role

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => userAPI.getUnreadCount(),
  });

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    navigate('/login');
  };

  const isActive = (href: string) => {
    return location.pathname === href || location.pathname.startsWith(href + '/');
  };

  const filteredNavigation = navigation.filter(item => {
    if (!item.roles) return true;
    return item.roles.includes(userRole);
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div
        className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'
          }`}
      >
        <div
          className="fixed inset-0 bg-gray-900/80"
          onClick={() => setSidebarOpen(false)}
        />
        <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-xl overflow-y-auto">
          <div className="flex items-center justify-between h-16 px-4 border-b">
            <span className="text-xl font-bold text-primary-600">GSTONGO</span>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-md hover:bg-gray-100"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>
          <nav className="p-4 space-y-1">
            {filteredNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg ${isActive(item.href)
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                  }`}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            ))}
          </nav>
          <div className="p-4 border-t">
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-3 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
          <div className="flex items-center h-16 px-6 border-b">
            <span className="text-xl font-bold text-primary-600">GSTONGO</span>
          </div>
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {filteredNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${isActive(item.href)
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                  }`}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            ))}
          </nav>
          <div className="p-4 border-t">
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-3 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex items-center h-16 px-4 bg-white border-b shadow-sm lg:px-8">
          <button
            className="p-2 -ml-2 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="w-6 h-6" />
          </button>

          <div className="flex-1 flex items-center justify-end space-x-4">
            <button className="relative p-2 text-gray-500 hover:text-gray-700">
              <BellIcon className="w-6 h-6" />
              {notifications?.data?.unread_count > 0 && (
                <span className="absolute top-0 right-0 flex items-center justify-center w-5 h-5 text-xs text-white bg-red-500 rounded-full">
                  {notifications.data.unread_count}
                </span>
              )}
            </button>

            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <UserCircleIcon className="w-5 h-5 text-primary-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
