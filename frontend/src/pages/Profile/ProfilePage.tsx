/**
 * Profile Page Component
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { userAPI } from '../../services/api';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import toast from 'react-hot-toast';

const ProfilePage: React.FC = () => {
  const { data: profile, isLoading, refetch } = useQuery({
    queryKey: ['profile'],
    queryFn: () => userAPI.getProfile(),
  });
  
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  const updateMutation = useMutation({
    mutationFn: (data: any) => userAPI.updateProfile(data),
    onSuccess: () => {
      toast.success('Profile updated successfully!');
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Update failed');
    },
  });
  
  const profileData = profile?.data;
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
      
      {/* Personal Information */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={profileData?.email || ''}
              disabled
              className="input-field bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">CIN</label>
            <input
              type="text"
              value={profileData?.cin || ''}
              disabled
              className="input-field bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
            <input
              type="text"
              defaultValue={profileData?.first_name || ''}
              {...register('first_name')}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
            <input
              type="text"
              defaultValue={profileData?.last_name || ''}
              {...register('last_name')}
              className="input-field"
            />
          </div>
        </div>
      </div>
      
      {/* GST Details */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">GST Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">GST Number</label>
            <input
              type="text"
              defaultValue={profileData?.gst_number || ''}
              {...register('gst_number')}
              className="input-field"
              placeholder="27ABCDE1234F1Z5"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Legal Name</label>
            <input
              type="text"
              defaultValue={profileData?.legal_name || ''}
              {...register('legal_name')}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Trade Name</label>
            <input
              type="text"
              defaultValue={profileData?.trade_name || ''}
              {...register('trade_name')}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
            <input
              type="text"
              defaultValue={profileData?.state || ''}
              {...register('state')}
              className="input-field"
            />
          </div>
        </div>
      </div>
      
      {/* Address */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Address</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
            <input
              type="text"
              defaultValue={profileData?.address_line_1 || ''}
              {...register('address_line_1')}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 2</label>
            <input
              type="text"
              defaultValue={profileData?.address_line_2 || ''}
              {...register('address_line_2')}
              className="input-field"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
              <input
                type="text"
                defaultValue={profileData?.city || ''}
                {...register('city')}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
              <input
                type="text"
                defaultValue={profileData?.state || ''}
                {...register('state')}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Pincode</label>
              <input
                type="text"
                defaultValue={profileData?.pincode || ''}
                {...register('pincode')}
                className="input-field"
                maxLength={6}
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSubmit((data) => updateMutation.mutate(data))}
          disabled={updateMutation.isPending}
          className="btn-primary"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
};

export default ProfilePage;
