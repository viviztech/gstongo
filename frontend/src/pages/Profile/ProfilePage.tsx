/**
 * Profile Page Component
 */
import React, { useEffect, useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { userAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  UserCircleIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  BellIcon,
  KeyIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline';

const BUSINESS_TYPES = [
  'Individual',
  'Proprietorship',
  'Partnership',
  'Private Limited Company',
  'Public Limited Company',
  'LLP',
  'Trust',
  'Society',
];

const REGISTRATION_TYPES = [
  'Regular',
  'Composition',
  'Consumer',
  'Unregistered',
];

const NOTIFICATION_CHANNELS = [
  { value: 'email', label: 'Email' },
  { value: 'sms', label: 'SMS' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'push', label: 'Push Notification' },
];

const ProfilePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('personal');

  const { data: profile, isLoading, refetch } = useQuery({
    queryKey: ['profile'],
    queryFn: () => userAPI.getProfile(),
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm();
  // Separate form for password change
  const {
    register: registerPassword,
    handleSubmit: handleSubmitPassword,
    reset: resetPassword,
    formState: { errors: passwordErrors }
  } = useForm();

  const updateMutation = useMutation({
    mutationFn: (data: any) => userAPI.updateProfile(data),
    onSuccess: () => {
      toast.success('Profile updated successfully!');
      refetch();
    },
    onError: (error: any) => {
      const message = error.response?.data?.error?.message || 'Update failed';
      toast.error(message);
    },
  });

  const passwordMutation = useMutation({
    mutationFn: (data: any) => userAPI.changePassword(data),
    onSuccess: () => {
      toast.success('Password changed successfully!');
      resetPassword();
    },
    onError: (error: any) => {
      const message = error.response?.data?.error?.message || 'Password change failed';
      toast.error(message);
    },
  });

  const profileData = profile?.data;

  // Reset form when data is loaded
  useEffect(() => {
    if (profileData) {
      reset(profileData);
    }
  }, [profileData, reset]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const tabs = [
    { id: 'personal', label: 'Personal Info', icon: UserCircleIcon },
    { id: 'business', label: 'Business Details', icon: BuildingOfficeIcon },
    { id: 'address', label: 'Address', icon: MapPinIcon },
    { id: 'preferences', label: 'Preferences', icon: BellIcon },
    { id: 'security', label: 'Security', icon: KeyIcon },
  ];

  const onProfileSubmit = (data: any) => {
    updateMutation.mutate(data);
  };

  const onPasswordSubmit = (data: any) => {
    if (data.new_password !== data.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }
    passwordMutation.mutate({
      old_password: data.current_password,
      new_password: data.new_password
    });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
          <p className="text-gray-600">Manage your account settings and preferences</p>
        </div>
        <div className="text-sm font-medium text-primary-600 bg-primary-50 px-4 py-2 rounded-lg border border-primary-100">
          CIN: <span className="font-bold">{profileData?.cin}</span>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Sidebar Navigation */}
        <div className="w-full md:w-64 flex-shrink-0">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium transition-colors ${activeTab === tab.id
                    ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-4 border-transparent'
                  }`}
              >
                <tab.icon className={`w-5 h-5 mr-3 ${activeTab === tab.id ? 'text-primary-600' : 'text-gray-400'}`} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1">
          {activeTab !== 'security' ? (
            <form onSubmit={handleSubmit(onProfileSubmit)} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">

              {activeTab === 'personal' && (
                <div className="space-y-6 animate-fadeIn">
                  <h2 className="text-lg font-semibold text-gray-900 border-b pb-2">Personal Information</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                      <input
                        type="email"
                        value={profileData?.email || ''}
                        disabled
                        className="input-field bg-gray-50 text-gray-500 cursor-not-allowed"
                      />
                      <p className="mt-1 text-xs text-gray-500">Email cannot be changed contact support.</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                      <input
                        type="tel"
                        {...register('phone_number')}
                        className="input-field"
                        placeholder="+91 98765 43210"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                      <input
                        type="text"
                        {...register('first_name')}
                        className="input-field"
                        placeholder="John"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                      <input
                        type="text"
                        {...register('last_name')}
                        className="input-field"
                        placeholder="Doe"
                      />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'business' && (
                <div className="space-y-6 animate-fadeIn">
                  <h2 className="text-lg font-semibold text-gray-900 border-b pb-2">Business & GST Details</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Legal Name</label>
                      <input
                        type="text"
                        {...register('legal_name')}
                        className="input-field"
                        placeholder="Company Name Private Limited"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">GST Number</label>
                      <input
                        type="text"
                        {...register('gst_number')}
                        className="input-field uppercase"
                        placeholder="27ABCDE1234F1Z5"
                        maxLength={15}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Trade Name</label>
                      <input
                        type="text"
                        {...register('trade_name')}
                        className="input-field"
                        placeholder="Brand Name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Business Type</label>
                      <select {...register('business_type')} className="input-field">
                        <option value="">Select Business Type</option>
                        {BUSINESS_TYPES.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Registration Type</label>
                      <select {...register('registration_type')} className="input-field">
                        <option value="">Select Registration Type</option>
                        {REGISTRATION_TYPES.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Date of Registration</label>
                      <input
                        type="date"
                        {...register('date_of_registration')}
                        className="input-field"
                      />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'address' && (
                <div className="space-y-6 animate-fadeIn">
                  <h2 className="text-lg font-semibold text-gray-900 border-b pb-2">Registered Address</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
                      <input
                        type="text"
                        {...register('address_line_1')}
                        className="input-field"
                        placeholder="Building, Street Name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 2</label>
                      <input
                        type="text"
                        {...register('address_line_2')}
                        className="input-field"
                        placeholder="Area, Locality"
                      />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                        <input
                          type="text"
                          {...register('city')}
                          className="input-field"
                          placeholder="City"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                        <input
                          type="text"
                          {...register('state')}
                          className="input-field"
                          placeholder="State"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
                        <input
                          type="text"
                          {...register('pincode')}
                          className="input-field"
                          placeholder="400001"
                          maxLength={6}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'preferences' && (
                <div className="space-y-6 animate-fadeIn">
                  <h2 className="text-lg font-semibold text-gray-900 border-b pb-2">Account Preferences</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Notification Channel</label>
                      <select {...register('preferred_notification_channel')} className="input-field">
                        {NOTIFICATION_CHANNELS.map(channel => (
                          <option key={channel.value} value={channel.value}>{channel.label}</option>
                        ))}
                      </select>
                      <p className="mt-1 text-xs text-gray-500">How would you like to receive updates?</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end pt-4 border-t mt-6">
                <button
                  type="submit"
                  disabled={updateMutation.isPending}
                  className="btn-primary min-w-[150px]"
                >
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleSubmitPassword(onPasswordSubmit)} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6 animate-fadeIn">
              <h2 className="text-lg font-semibold text-gray-900 border-b pb-2">Security Settings</h2>

              <div className="max-w-md space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                  <input
                    type="password"
                    {...registerPassword('current_password', { required: 'Current password is required' })}
                    className="input-field"
                  />
                  {passwordErrors.current_password && (
                    <p className="text-red-500 text-xs mt-1">{passwordErrors.current_password.message as string}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                  <input
                    type="password"
                    {...registerPassword('new_password', {
                      required: 'New password is required',
                      minLength: { value: 8, message: 'Password must be at least 8 characters' }
                    })}
                    className="input-field"
                  />
                  {passwordErrors.new_password && (
                    <p className="text-red-500 text-xs mt-1">{passwordErrors.new_password.message as string}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                  <input
                    type="password"
                    {...registerPassword('confirm_password', { required: 'Please confirm your password' })}
                    className="input-field"
                  />
                  {passwordErrors.confirm_password && (
                    <p className="text-red-500 text-xs mt-1">{passwordErrors.confirm_password.message as string}</p>
                  )}
                </div>

                <div className="pt-4">
                  <button
                    type="submit"
                    disabled={passwordMutation.isPending}
                    className="btn-primary w-full"
                  >
                    {passwordMutation.isPending ? 'Updating...' : 'Change Password'}
                  </button>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
