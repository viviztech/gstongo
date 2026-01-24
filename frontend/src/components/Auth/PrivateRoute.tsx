/**
 * Private Route Component
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { userAPI } from '../../services/api';

interface PrivateRouteProps {
  children: React.ReactNode;
  roles?: string[];
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children, roles }) => {
  const location = useLocation();
  const token = localStorage.getItem('accessToken');
  
  // Check if user is authenticated
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // Fetch user profile to check roles
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => userAPI.getProfile(),
    enabled: !!token,
  });
  
  if (isLoading) {
    return null; // Or show loading spinner
  }
  
  // Check role-based access
  if (roles && roles.length > 0) {
    const userRole = profile?.data?.is_staff ? 'admin' : 'user';
    if (!roles.includes(userRole)) {
      return <Navigate to="/dashboard" replace />;
    }
  }
  
  return <>{children}</>;
};

export default PrivateRoute;
