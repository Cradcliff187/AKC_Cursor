'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import { generateMaterialsReceiptId, generateActivityLogId } from '@/lib/utils';

type FormData = {
  receiptdate: string;
  vendorname: string;
  invoicenumber: string;
  description: string;
  totalamount: number;
  receiptnotes: string;
  taxamount: number;
};

export default function NewMaterialsReceiptPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.projectId as string;
  
  const { register, handleSubmit, formState: { errors }, watch } = useForm<FormData>({
    defaultValues: {
      receiptdate: new Date().toISOString().split('T')[0],
      taxamount: 0,
    },
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [projectName, setProjectName] = useState<string>('');
  
  // Watch form values to update the total
  const totalAmount = watch('totalamount');
  const taxAmount = watch('taxamount');
  
  useEffect(() => {
    const fetchProjectDetails = async () => {
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
      } catch (error: any) {
        console.error('Error fetching project details:', error);
        setError(error.message);
      }
    };
    
    fetchProjectDetails();
  }, [projectId]);
  
  const onSubmit = async (data: FormData) => {
    try {
      setIsSubmitting(true);
      setError(null);
      
      const receiptId = generateMaterialsReceiptId();
      const newReceipt = {
        receiptid: receiptId,
        projectid: projectId,
        receiptdate: data.receiptdate,
        vendorname: data.vendorname,
        invoicenumber: data.invoicenumber,
        description: data.description,
        totalamount: data.totalamount,
        taxamount: data.taxamount || 0,
        grandtotal: (parseFloat(data.totalamount.toString()) + parseFloat((data.taxamount || 0).toString())),
        receiptnotes: data.receiptnotes,
        createdby: (await supabase.auth.getUser()).data.user?.email || 'Unknown',
        createdon: new Date().toISOString(),
      };
      
      const { error: insertError } = await supabase
        .from('materialsreceipts')
        .insert(newReceipt);
      
      if (insertError) {
        throw insertError;
      }
      
      // Log activity
      await supabase
        .from('activitylog')
        .insert({
          logid: generateActivityLogId(),
          timestamp: new Date().toISOString(),
          action: 'Materials Receipt Created',
          useremail: (await supabase.auth.getUser()).data.user?.email,
          moduletype: 'Materials',
          referenceid: receiptId,
          detailsjson: JSON.stringify(newReceipt),
        });
      
      router.push(`/projects/${projectId}`);
    } catch (error: any) {
      console.error('Error creating materials receipt:', error);
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Add Materials Receipt</h1>
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
              <label htmlFor="receiptdate" className="block text-sm font-medium text-gray-700">
                Receipt Date *
              </label>
              <div className="mt-1">
                <input
                  type="date"
                  id="receiptdate"
                  {...register('receiptdate', { required: 'Receipt date is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.receiptdate && (
                  <p className="mt-1 text-sm text-red-600">{errors.receiptdate.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="vendorname" className="block text-sm font-medium text-gray-700">
                Vendor Name *
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="vendorname"
                  {...register('vendorname', { required: 'Vendor name is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.vendorname && (
                  <p className="mt-1 text-sm text-red-600">{errors.vendorname.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="invoicenumber" className="block text-sm font-medium text-gray-700">
                Invoice Number
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="invoicenumber"
                  {...register('invoicenumber')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description *
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="description"
                  {...register('description', { required: 'Description is required' })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label htmlFor="totalamount" className="block text-sm font-medium text-gray-700">
                Amount (before tax) *
              </label>
              <div className="mt-1">
                <input
                  type="number"
                  id="totalamount"
                  step="0.01"
                  min="0"
                  {...register('totalamount', { 
                    required: 'Amount is required',
                    min: { value: 0, message: 'Amount must be positive' },
                    valueAsNumber: true
                  })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.totalamount && (
                  <p className="mt-1 text-sm text-red-600">{errors.totalamount.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label htmlFor="taxamount" className="block text-sm font-medium text-gray-700">
                Tax Amount
              </label>
              <div className="mt-1">
                <input
                  type="number"
                  id="taxamount"
                  step="0.01"
                  min="0"
                  {...register('taxamount', { 
                    min: { value: 0, message: 'Tax amount must be positive' },
                    valueAsNumber: true
                  })}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                {errors.taxamount && (
                  <p className="mt-1 text-sm text-red-600">{errors.taxamount.message}</p>
                )}
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">
                Grand Total
              </label>
              <div className="mt-1">
                <div className="py-2 px-3 bg-gray-50 rounded-md">
                  <span className="text-gray-900 font-medium">
                    ${(parseFloat(totalAmount || 0) + parseFloat(taxAmount || 0)).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="sm:col-span-6">
              <label htmlFor="receiptnotes" className="block text-sm font-medium text-gray-700">
                Notes
              </label>
              <div className="mt-1">
                <textarea
                  id="receiptnotes"
                  rows={3}
                  {...register('receiptnotes')}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                ></textarea>
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
                {isSubmitting ? 'Saving...' : 'Add Receipt'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </AppLayout>
  );
} 