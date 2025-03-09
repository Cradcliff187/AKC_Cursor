'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import { generateTimeLogId, generateActivityLogId } from '@/lib/utils';

type FormData = {
  employeeid: string;
  hours: number;
  entrydate: string;
  description: string;
  hourlyrate: number;
};

type Employee = {
  employeeid: string;
  firstname: string;
  lastname: string;
};

export default function NewTimeLogPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.projectId as string;
  
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      entrydate: new Date().toISOString().split('T')[0],
    },
  });
  
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [projectName, setProjectName] = useState<string>('');
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch project details
        const { data: projectData, error: projectError } = await supabase
          .from('projects')
          .select('projectname')
          .eq('projectid', projectId)
          .single();
        
        if (projectError) {
          throw projectError;
        }
        
        setProjectName(projectData.projectname);
        
        // Fetch employees
        const { data: employeeData, error: employeeError } = await supabase
          .from('employees')
          .select('employeeid, firstname, lastname')
          .eq('status', 'Active')
          .order('lastname', { ascending: true });
        
        if (employeeError) {
          throw employeeError;
        }
        
        setEmployees(employeeData || []);
      } catch (error: any) {
        console.error('Error fetching data:', error);
        setError(error.message);
      }
    };
    
    fetchData();
  }, [projectId]);
  
  const onSubmit = async (data: FormData) => {
    try {
      setIsSubmitting(true);
      setError(null);
      
      const timeLogId = generateTimeLogId();
      const newTimeLog = {
        timeid: timeLogId,
        projectid: projectId,
        employeeid: data.employeeid,
        hours: data.hours,
        entrydate: data.entrydate,
        description: data.description,
        hourlyrate: data.hourlyrate,
        totalamount: data.hours * data.hourlyrate,
        createdby: (await supabase.auth.getUser()).data.user?.email || 'Unknown',
        createdon: new Date().toISOString(),
      };
      
      const { error: insertError } = await supabase
        .from('timelogs')
        .insert(newTimeLog);
      
      if (insertError) {
        throw insertError;
      }
      
      // Log activity
      await supabase
        .from('activitylog')
        .insert({
          logid: generateActivityLogId(),
          timestamp: new Date().toISOString(),
          action: 'Time Log Created',
          useremail: (await supabase.auth.getUser()).data.user?.email,
          moduletype: 'Time Logs',
          referenceid: timeLogId,
          detailsjson: JSON.stringify(newTimeLog),
        });
      
      router.push(`/projects/${projectId}`);
    } catch (error: any) {
      console.error('Error creating time log:', error);
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Add Time Log</h1>
          <p className="mt-2 text-sm text-gray-700">
            Project: {projectName}
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
              <label htmlFor="employeeid" className="block text-sm font-medium text-gray-700">
                Employee *
              </label>
              <div className="mt-1">
                <select
                  id="employeeid"
                  {...register('employeeid', { required: 'Employee is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">Select Employee</option>
                  {employees.map((employee) => (
                    <option key={employee.employeeid} value={employee.employeeid}>
                      {employee.lastname}, {employee.firstname}
                    </option>
                  ))}
                </select>
                {errors.employeeid && (
                  <p className="mt-1 text-sm text-red-600">{errors.employeeid.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="entrydate" className="block text-sm font-medium text-gray-700">
                Date *
              </label>
              <div className="mt-1">
                <input
                  type="date"
                  id="entrydate"
                  {...register('entrydate', { required: 'Date is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.entrydate && (
                  <p className="mt-1 text-sm text-red-600">{errors.entrydate.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="hours" className="block text-sm font-medium text-gray-700">
                Hours *
              </label>
              <div className="mt-1">
                <input
                  type="number"
                  id="hours"
                  step="0.25"
                  min="0.25"
                  {...register('hours', { 
                    required: 'Hours are required',
                    min: { value: 0.25, message: 'Minimum 0.25 hours' },
                    valueAsNumber: true
                  })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.hours && (
                  <p className="mt-1 text-sm text-red-600">{errors.hours.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="hourlyrate" className="block text-sm font-medium text-gray-700">
                Hourly Rate ($) *
              </label>
              <div className="mt-1">
                <input
                  type="number"
                  id="hourlyrate"
                  step="0.01"
                  min="0"
                  {...register('hourlyrate', { 
                    required: 'Hourly rate is required',
                    min: { value: 0, message: 'Rate must be positive' },
                    valueAsNumber: true
                  })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.hourlyrate && (
                  <p className="mt-1 text-sm text-red-600">{errors.hourlyrate.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-6">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description *
              </label>
              <div className="mt-1">
                <textarea
                  id="description"
                  rows={3}
                  {...register('description', { required: 'Description is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                ></textarea>
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>
            </div>
          </div>
          
          <div className="pt-5">
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => router.push(`/projects/${projectId}`)}
                className="btn btn-outline"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary"
              >
                {isSubmitting ? 'Saving...' : 'Add Time Log'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </AppLayout>
  );
} 