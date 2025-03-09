'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import type { Customer } from '@/lib/supabase';
import { PROJECT_STATUSES } from '@/lib/constants';
import { generateProjectId, generateActivityLogId } from '@/lib/utils';

type FormData = {
  projectname: string;
  customerid: string;
  jobdescription: string;
  status: string;
  sitelocationaddress: string;
  sitelocationcity: string;
  sitelocationstate: string;
  sitelocationzip: string;
};

export default function NewProjectPage() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      status: PROJECT_STATUSES.PENDING
    }
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [nextSequence, setNextSequence] = useState<number>(1);

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const { data, error } = await supabase
          .from('customers')
          .select('*')
          .order('customername', { ascending: true });
          
        if (error) {
          throw error;
        }

        setCustomers(data || []);
      } catch (error: any) {
        console.error('Error fetching customers:', error);
        setError(error.message);
      }
    };

    const fetchNextSequence = async () => {
      try {
        // Get the current year and month
        const date = new Date();
        const year = date.getFullYear().toString().slice(-2);
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const prefix = `PROJ-${year}${month}`;
        
        // Get the highest sequence number for this month
        const { data, error } = await supabase
          .from('projects')
          .select('projectid')
          .like('projectid', `${prefix}%`)
          .order('projectid', { ascending: false });
        
        if (error) {
          throw error;
        }
        
        // Extract the sequence number from the highest projectid
        if (data && data.length > 0) {
          const latestId = data[0].projectid;
          const sequencePart = latestId.split('-')[2];
          setNextSequence(parseInt(sequencePart) + 1);
        } else {
          setNextSequence(1);
        }
      } catch (error: any) {
        console.error('Error fetching next sequence:', error);
      }
    };

    fetchCustomers();
    fetchNextSequence();
  }, []);

  const onSubmit = async (data: FormData) => {
    try {
      setIsSubmitting(true);
      setError(null);

      // Find the selected customer
      const selectedCustomer = customers.find(c => c.customerid === data.customerid);
      
      const projectId = generateProjectId(nextSequence);
      const newProject = {
        projectid: projectId,
        projectname: data.projectname,
        customerid: data.customerid,
        customername: selectedCustomer?.customername,
        jobdescription: data.jobdescription,
        status: data.status,
        sitelocationaddress: data.sitelocationaddress,
        sitelocationcity: data.sitelocationcity,
        sitelocationstate: data.sitelocationstate,
        sitelocationzip: data.sitelocationzip,
        createdby: (await supabase.auth.getUser()).data.user?.email || 'Unknown',
        createdon: new Date().toISOString(),
      };

      const { error: insertError } = await supabase
        .from('projects')
        .insert(newProject);

      if (insertError) {
        throw insertError;
      }

      // Log activity
      await supabase
        .from('activitylog')
        .insert({
          logid: generateActivityLogId(),
          timestamp: new Date().toISOString(),
          action: 'Project Created',
          useremail: (await supabase.auth.getUser()).data.user?.email,
          moduletype: 'Projects',
          referenceid: projectId,
          detailsjson: JSON.stringify(newProject),
          status: data.status,
        });

      router.push('/projects');
    } catch (error: any) {
      console.error('Error creating project:', error);
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">New Project</h1>
          <p className="mt-2 text-sm text-gray-700">
            Create a new construction project.
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
            <div className="sm:col-span-3">
              <label htmlFor="projectname" className="block text-sm font-medium text-gray-700">
                Project Name *
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="projectname"
                  {...register('projectname', { required: 'Project name is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.projectname && (
                  <p className="mt-1 text-sm text-red-600">{errors.projectname.message}</p>
                )}
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="customerid" className="block text-sm font-medium text-gray-700">
                Customer *
              </label>
              <div className="mt-1">
                <select
                  id="customerid"
                  {...register('customerid', { required: 'Customer is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">Select a customer</option>
                  {customers.map((customer) => (
                    <option key={customer.customerid} value={customer.customerid}>
                      {customer.customername}
                    </option>
                  ))}
                </select>
                {errors.customerid && (
                  <p className="mt-1 text-sm text-red-600">{errors.customerid.message}</p>
                )}
              </div>
            </div>

            <div className="sm:col-span-6">
              <label htmlFor="jobdescription" className="block text-sm font-medium text-gray-700">
                Job Description
              </label>
              <div className="mt-1">
                <textarea
                  id="jobdescription"
                  rows={3}
                  {...register('jobdescription')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                Status *
              </label>
              <div className="mt-1">
                <select
                  id="status"
                  {...register('status', { required: 'Status is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value={PROJECT_STATUSES.PENDING}>{PROJECT_STATUSES.PENDING}</option>
                  <option value={PROJECT_STATUSES.APPROVED}>{PROJECT_STATUSES.APPROVED}</option>
                  <option value={PROJECT_STATUSES.IN_PROGRESS}>{PROJECT_STATUSES.IN_PROGRESS}</option>
                </select>
                {errors.status && (
                  <p className="mt-1 text-sm text-red-600">{errors.status.message}</p>
                )}
              </div>
            </div>

            <div className="sm:col-span-6">
              <h3 className="text-lg font-medium text-gray-700 mb-3">Site Location</h3>
            </div>

            <div className="sm:col-span-6">
              <label htmlFor="sitelocationaddress" className="block text-sm font-medium text-gray-700">
                Address
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="sitelocationaddress"
                  {...register('sitelocationaddress')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="sitelocationcity" className="block text-sm font-medium text-gray-700">
                City
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="sitelocationcity"
                  {...register('sitelocationcity')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="sitelocationstate" className="block text-sm font-medium text-gray-700">
                State
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="sitelocationstate"
                  {...register('sitelocationstate')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="sitelocationzip" className="block text-sm font-medium text-gray-700">
                ZIP
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="sitelocationzip"
                  {...register('sitelocationzip')}
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
                {isSubmitting ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </AppLayout>
  );
} 