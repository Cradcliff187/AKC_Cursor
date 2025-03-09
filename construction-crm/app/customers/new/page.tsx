'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { v4 as uuidv4 } from 'uuid';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import { CUSTOMER_STATUSES } from '@/lib/constants';
import { generateCustomerId, generateActivityLogId } from '@/lib/utils';

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

export default function NewCustomerPage() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      status: CUSTOMER_STATUSES.ACTIVE
    }
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nextSequence, setNextSequence] = useState<number>(1);

  React.useEffect(() => {
    const fetchNextSequence = async () => {
      try {
        // Get the current year
        const year = new Date().getFullYear().toString().slice(-2);
        const prefix = `${year}-`;
        
        // Get the highest sequence number for this year
        const { data, error } = await supabase
          .from('customers')
          .select('customerid')
          .like('customerid', `${prefix}%`)
          .order('customerid', { ascending: false });
        
        if (error) {
          throw error;
        }
        
        // Extract the sequence number from the highest customerid
        if (data && data.length > 0) {
          const latestId = data[0].customerid;
          const sequencePart = latestId.split('-')[1];
          setNextSequence(parseInt(sequencePart) + 1);
        } else {
          setNextSequence(1);
        }
      } catch (error: any) {
        console.error('Error fetching next sequence:', error);
      }
    };

    fetchNextSequence();
  }, []);

  const onSubmit = async (data: FormData) => {
    try {
      setIsSubmitting(true);
      setError(null);
      
      const customerId = generateCustomerId(nextSequence);
      const newCustomer = {
        customerid: customerId,
        customername: data.customername,
        address: data.address,
        city: data.city,
        state: data.state,
        zip: data.zip,
        contactemail: data.contactemail,
        phone: data.phone,
        status: data.status,
        createdby: (await supabase.auth.getUser()).data.user?.email || 'Unknown',
        createdon: new Date().toISOString(),
      };

      const { error: insertError } = await supabase
        .from('customers')
        .insert(newCustomer);

      if (insertError) {
        throw insertError;
      }

      // Log activity
      await supabase
        .from('activitylog')
        .insert({
          logid: generateActivityLogId(),
          timestamp: new Date().toISOString(),
          action: 'Customer Created',
          useremail: (await supabase.auth.getUser()).data.user?.email,
          moduletype: 'Customers',
          referenceid: customerId,
          detailsjson: JSON.stringify(newCustomer),
          status: data.status,
        });

      router.push('/customers');
    } catch (error: any) {
      console.error('Error creating customer:', error);
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">New Customer</h1>
          <p className="mt-2 text-sm text-gray-700">
            Add a new customer to your account.
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
                {isSubmitting ? 'Creating...' : 'Create Customer'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </AppLayout>
  );
} 