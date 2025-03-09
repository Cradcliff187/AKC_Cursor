'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import type { Customer, Project } from '@/lib/supabase';
import { PROJECT_STATUSES } from '@/lib/constants';
import { generateActivityLogId } from '@/lib/utils';

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

type ProjectEditProps = {
  params: {
    projectId: string;
  };
};

export default function EditProjectPage({ params }: ProjectEditProps) {
  const { projectId } = params;
  const router = useRouter();
  const { register, handleSubmit, formState: { errors }, reset } = useForm<FormData>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch project details
        const { data: projectData, error: projectError } = await supabase
          .from('projects')
          .select('*')
          .eq('projectid', projectId)
          .single();
        
        if (projectError) throw projectError;
        setProject(projectData);

        // Initialize form with project data
        reset({
          projectname: projectData.projectname || '',
          customerid: projectData.customerid || '',
          jobdescription: projectData.jobdescription || '',
          status: projectData.status || PROJECT_STATUSES.PENDING,
          sitelocationaddress: projectData.sitelocationaddress || '',
          sitelocationcity: projectData.sitelocationcity || '',
          sitelocationstate: projectData.sitelocationstate || '',
          sitelocationzip: projectData.sitelocationzip || '',
        });

        // Fetch customers for the dropdown
        const { data: customersData, error: customersError } = await supabase
          .from('customers')
          .select('*')
          .order('customername', { ascending: true });
          
        if (customersError) throw customersError;
        setCustomers(customersData || []);
      } catch (error: any) {
        console.error('Error fetching data:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [projectId, reset]);

  const onSubmit = async (data: FormData) => {
    try {
      setIsSubmitting(true);
      setError(null);

      if (!project) {
        throw new Error("Project not found");
      }

      // Find the selected customer for storing customer name
      const selectedCustomer = customers.find(c => c.customerid === data.customerid);
      
      const updatedProject = {
        projectname: data.projectname,
        customerid: data.customerid,
        customername: selectedCustomer?.customername,
        jobdescription: data.jobdescription,
        status: data.status,
        sitelocationaddress: data.sitelocationaddress,
        sitelocationcity: data.sitelocationcity,
        sitelocationstate: data.sitelocationstate,
        sitelocationzip: data.sitelocationzip,
        lastmodified: new Date().toISOString(),
        lastmodifiedby: (await supabase.auth.getUser()).data.user?.email || 'Unknown',
      };

      const { error: updateError } = await supabase
        .from('projects')
        .update(updatedProject)
        .eq('projectid', projectId);

      if (updateError) {
        throw updateError;
      }

      // Log activity
      await supabase
        .from('activitylog')
        .insert({
          logid: generateActivityLogId(),
          timestamp: new Date().toISOString(),
          action: 'Project Updated',
          useremail: (await supabase.auth.getUser()).data.user?.email,
          moduletype: 'Projects',
          referenceid: projectId,
          detailsjson: JSON.stringify({
            before: project,
            after: { ...project, ...updatedProject }
          }),
          status: data.status,
          previousstatus: project.status
        });

      router.push(`/projects/${projectId}`);
    } catch (error: any) {
      console.error('Error updating project:', error);
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-500">Loading project details...</p>
        </div>
      </AppLayout>
    );
  }

  if (error && !project) {
    return (
      <AppLayout>
        <div className="bg-red-50 p-4 rounded-md mb-4">
          <div className="flex">
            <div>
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-2">{error}</p>
              <button
                onClick={() => router.push('/projects')}
                className="mt-4 bg-white text-sm text-red-600 px-4 py-2 border border-red-300 rounded-md shadow-sm hover:bg-red-50"
              >
                Back to Projects
              </button>
            </div>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex items-center mb-6">
        <button
          onClick={() => router.back()}
          className="mr-4 text-gray-500 hover:text-gray-700"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Edit Project</h1>
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
                  <option value={PROJECT_STATUSES.COMPLETED}>{PROJECT_STATUSES.COMPLETED}</option>
                  <option value={PROJECT_STATUSES.CANCELED}>{PROJECT_STATUSES.CANCELED}</option>
                  <option value={PROJECT_STATUSES.CLOSED}>{PROJECT_STATUSES.CLOSED}</option>
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
                {isSubmitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </AppLayout>
  );
} 