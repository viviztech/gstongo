/**
 * Private Route Component
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

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

  // For role-based access, we don't fetch profile here to avoid re-fetching
  // The profile should be fetched by the page/component that needs it
  // Role checking will be done by the individual pages

  return <>{children}</>;
};

export default PrivateRoute;
