'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import { CUSTOMER_STATUSES } from '@/lib/constants';
import { generateActivityLogId } from '@/lib/utils';

type FormData = {
  customername: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  contactemail: string;
  phone: string;
  status: string;
};

export default function EditCustomerPage() {
  const router = useRouter();
  const params = useParams();
  const customerId = params.customerId as string;
  
  const { register, handleSubmit, formState: { errors }, reset } = useForm<FormData>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchCustomer = async () => {
      try {
        setLoading(true);
        
        const { data, error } = await supabase
          .from('customers')
          .select('*')
          .eq('customerid', customerId)
          .single();
        
        if (error) {
          throw error;
        }
        
        // Set form values
        reset({
          customername: data.customername,
          address: data.address || '',
          city: data.city || '',
          state: data.state || '',
          zip: data.zip || '',
          contactemail: data.contactemail || '',
          phone: data.phone || '',
          status: data.status,
        });
      } catch (error: any) {
        console.error('Error fetching customer:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (customerId) {
      fetchCustomer();
    }
  }, [customerId, reset]);
  
  const onSubmit = async (data: FormData) => {
    try {
      setIsSubmitting(true);
      setError(null);
      
      const updates = {
        customername: data.customername,
        address: data.address,
        city: data.city,
        state: data.state,
        zip: data.zip,
        contactemail: data.contactemail,
        phone: data.phone,
        status: data.status,
        updatedon: new Date().toISOString(),
        updatedby: (await supabase.auth.getUser()).data.user?.email || 'Unknown',
      };
      
      const { error: updateError } = await supabase
        .from('customers')
        .update(updates)
        .eq('customerid', customerId);
      
      if (updateError) {
        throw updateError;
      }
      
      // Log activity
      await supabase
        .from('activitylog')
        .insert({
          logid: generateActivityLogId(),
          timestamp: new Date().toISOString(),
          action: 'Customer Updated',
          useremail: (await supabase.auth.getUser()).data.user?.email,
          moduletype: 'Customers',
          referenceid: customerId,
          detailsjson: JSON.stringify(updates),
          status: data.status,
        });
      
      router.push(`/customers/${customerId}`);
    } catch (error: any) {
      console.error('Error updating customer:', error);
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      </AppLayout>
    );
  }
  
  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Edit Customer</h1>
          <p className="mt-2 text-sm text-gray-700">
            Update customer information.
          </p>
        </div>
      </div>
      
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <form onSubmit={handleSubmit(onSubmit)} className="p-6">
          {error && (
            <div className="mb-4 bg-red-50 p-4 rounded-md">
              <div className="flex">
                <div>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-4">
              <label htmlFor="customername" className="block text-sm font-medium text-gray-700">
                Customer Name *
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="customername"
                  {...register('customername', { required: 'Customer name is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.customername && (
                  <p className="mt-1 text-sm text-red-600">{errors.customername.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                Status *
              </label>
              <div className="mt-1">
                <select
                  id="status"
                  {...register('status', { required: 'Status is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value={CUSTOMER_STATUSES.ACTIVE}>{CUSTOMER_STATUSES.ACTIVE}</option>
                  <option value={CUSTOMER_STATUSES.INACTIVE}>{CUSTOMER_STATUSES.INACTIVE}</option>
                  <option value={CUSTOMER_STATUSES.PENDING}>{CUSTOMER_STATUSES.PENDING}</option>
                </select>
                {errors.status && (
                  <p className="mt-1 text-sm text-red-600">{errors.status.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-6">
              <label htmlFor="address" className="block text-sm font-medium text-gray-700">
                Address
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="address"
                  {...register('address')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label htmlFor="city" className="block text-sm font-medium text-gray-700">
                City
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="city"
                  {...register('city')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label htmlFor="state" className="block text-sm font-medium text-gray-700">
                State
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="state"
                  {...register('state')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label htmlFor="zip" className="block text-sm font-medium text-gray-700">
                ZIP
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="zip"
                  {...register('zip')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="contactemail" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <div className="mt-1">
                <input
                  type="email"
                  id="contactemail"
                  {...register('contactemail', {
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: "Invalid email address"
                    }
                  })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.contactemail && (
                  <p className="mt-1 text-sm text-red-600">{errors.contactemail.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                Phone
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="phone"
                  {...register('phone')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>
          
          <div className="pt-5">
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => router.back()}
                className="btn btn-outline"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary"
              >
                {isSubmitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </AppLayout>
  );
} 