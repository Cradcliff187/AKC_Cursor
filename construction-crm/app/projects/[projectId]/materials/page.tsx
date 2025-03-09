'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import Link from 'next/link';

type MaterialsReceipt = {
  receiptid: string;
  projectid: string;
  receiptdate: string;
  vendorname: string;
  invoicenumber: string;
  description: string;
  totalamount: number;
  taxamount: number;
  grandtotal: number;
  receiptnotes: string;
  createdon: string;
  createdby: string;
};

type Project = {
  projectid: string;
  projectname: string;
};

export default function MaterialsReceiptsPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.projectId as string;
  
  const [receipts, setReceipts] = useState<MaterialsReceipt[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [vendorFilter, setVendorFilter] = useState<string>('');
  const [vendors, setVendors] = useState<string[]>([]);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch project details
        const { data: projectData, error: projectError } = await supabase
          .from('projects')
          .select('projectid, projectname')
          .eq('projectid', projectId)
          .single();
        
        if (projectError) {
          throw projectError;
        }
        
        setProject(projectData);
        
        // Fetch materials receipts
        const { data: receiptsData, error: receiptsError } = await supabase
          .from('materialsreceipts')
          .select('*')
          .eq('projectid', projectId)
          .order('receiptdate', { ascending: false });
        
        if (receiptsError) {
          throw receiptsError;
        }
        
        setReceipts(receiptsData || []);
        
        // Extract unique vendors for filter dropdown
        const uniqueVendors = Array.from(
          new Set(receiptsData?.map(receipt => receipt.vendorname))
        ).filter(Boolean) as string[];
        
        setVendors(uniqueVendors);
      } catch (error: any) {
        console.error('Error fetching materials receipts:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [projectId]);
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };
  
  const formatCurrency = (amount: number) => {
    return amount.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
    });
  };
  
  const filterReceipts = () => {
    return receipts.filter(receipt => {
      // Apply date filter if both start and end dates are provided
      const dateMatch = startDate && endDate
        ? new Date(receipt.receiptdate) >= new Date(startDate) && new Date(receipt.receiptdate) <= new Date(endDate)
        : true;
      
      // Apply vendor filter if selected
      const vendorMatch = vendorFilter
        ? receipt.vendorname === vendorFilter
        : true;
      
      return dateMatch && vendorMatch;
    });
  };
  
  const clearFilters = () => {
    setStartDate('');
    setEndDate('');
    setVendorFilter('');
  };
  
  const calculateTotalAmount = (receipts: MaterialsReceipt[]) => {
    return receipts.reduce((total, receipt) => total + receipt.grandtotal, 0);
  };
  
  const filteredReceipts = filterReceipts();
  
  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      </AppLayout>
    );
  }
  
  if (error || !project) {
    return (
      <AppLayout>
        <div className="bg-red-50 p-4 rounded-md">
          <div className="flex">
            <div>
              <p className="text-sm text-red-700">
                {error || 'Project not found'}
              </p>
            </div>
          </div>
        </div>
        <div className="mt-4">
          <button
            type="button"
            onClick={() => router.push('/projects')}
            className="btn btn-outline"
          >
            Back to Projects
          </button>
        </div>
      </AppLayout>
    );
  }
  
  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Materials Receipts</h1>
          <p className="mt-2 text-sm text-gray-700">
            Project: {project.projectname}
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <Link
            href={`/projects/${projectId}/materials/new`}
            className="btn btn-primary"
          >
            Add Receipt
          </Link>
          <Link
            href={`/projects/${projectId}`}
            className="btn btn-outline"
          >
            Back to Project
          </Link>
        </div>
      </div>
      
      <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Filter Receipts</h2>
          
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-2">
              <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">
                Start Date
              </label>
              <div className="mt-1">
                <input
                  type="date"
                  id="startDate"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">
                End Date
              </label>
              <div className="mt-1">
                <input
                  type="date"
                  id="endDate"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>
            
            <div className="sm:col-span-2">
              <label htmlFor="vendorFilter" className="block text-sm font-medium text-gray-700">
                Vendor
              </label>
              <div className="mt-1">
                <select
                  id="vendorFilter"
                  value={vendorFilter}
                  onChange={(e) => setVendorFilter(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">All Vendors</option>
                  {vendors.map((vendor) => (
                    <option key={vendor} value={vendor}>
                      {vendor}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="sm:col-span-6 flex justify-end">
              <button
                type="button"
                onClick={clearFilters}
                className="btn btn-outline"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {filteredReceipts.length === 0 ? (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-6 text-center">
            <p className="text-gray-500">
              No materials receipts found for this project.
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Summary</h2>
              
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-500">Total Receipts</p>
                  <p className="mt-1 text-3xl font-semibold text-gray-900">
                    {filteredReceipts.length}
                  </p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-500">Total Amount</p>
                  <p className="mt-1 text-3xl font-semibold text-gray-900">
                    {formatCurrency(calculateTotalAmount(filteredReceipts))}
                  </p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-500">Unique Vendors</p>
                  <p className="mt-1 text-3xl font-semibold text-gray-900">
                    {new Set(filteredReceipts.map(r => r.vendorname)).size}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vendor
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Invoice #
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tax
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredReceipts.map((receipt) => (
                  <tr key={receipt.receiptid}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatDate(receipt.receiptdate)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {receipt.vendorname}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {receipt.invoicenumber || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">
                      {receipt.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(receipt.totalamount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(receipt.taxamount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(receipt.grandtotal)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </AppLayout>
  );
} 