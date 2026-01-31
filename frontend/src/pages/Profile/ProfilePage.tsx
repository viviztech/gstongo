/**
 * Profile Page Component
 */
import React, { useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { userAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import toast from 'react-hot-toast';

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
  const { data: profile, isLoading, refetch } = useQuery({
    queryKey: ['profile'],
    queryFn: () => userAPI.getProfile(),
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm();

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

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <div className="text-sm font-medium text-primary-600 bg-primary-50 px-3 py-1 rounded-full">
          CIN: {profileData?.cin}
        </div>
      </div>

      <form onSubmit={handleSubmit((data) => updateMutation.mutate(data))} className="space-y-6">
        {/* Personal Information */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email (Read-only)</label>
              <input
                type="email"
                value={profileData?.email || ''}
                disabled
                className="input-field bg-gray-50 border-gray-200 text-gray-500 cursor-not-allowed"
              />
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

        {/* Business & GST Details */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Business & GST Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Legal Name (as per PAN/GST)</label>
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

        {/* Address */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Registered Address</h2>
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

        {/* Preferences */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Preferences</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Notification Channel</label>
              <select {...register('preferred_notification_channel')} className="input-field">
                {NOTIFICATION_CHANNELS.map(channel => (
                  <option key={channel.value} value={channel.value}>{channel.label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-4">
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="btn-primary min-w-[150px]"
          >
            {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProfilePage;
