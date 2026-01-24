/**
 * Auth Layout Component
 */
import React from 'react';
import { Outlet } from 'react-router-dom';

const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">GSTONGO</h1>
          <p className="text-primary-200 mt-2">GST Filing Made Simple</p>
        </div>
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <Outlet />
        </div>
        <p className="text-center text-primary-200 text-sm mt-6">
          © 2025 GSTONGO. All rights reserved.
        </p>
      </div>
    </div>
  );
};

export default AuthLayout;
