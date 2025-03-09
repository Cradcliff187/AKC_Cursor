'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import Link from 'next/link';

type Customer = {
  customerid: string;
  customername: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  contactemail: string;
  phone: string;
  status: string;
  createdon: string;
  createdby: string;
};

type Project = {
  projectid: string;
  projectname: string;
  status: string;
  createdon: string;
  estimatedcost: number;
  startdate: string | null;
  enddate: string | null;
};

export default function CustomerDetailPage() {
  const router = useRouter();
  const params = useParams();
  const customerId = params.customerId as string;
  
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchCustomerDetails = async () => {
      try {
        setLoading(true);
        
        // Fetch customer details
        const { data: customerData, error: customerError } = await supabase
          .from('customers')
          .select('*')
          .eq('customerid', customerId)
          .single();
        
        if (customerError) {
          throw customerError;
        }
        
        setCustomer(customerData);
        
        // Fetch customer's projects
        const { data: projectsData, error: projectsError } = await supabase
          .from('projects')
          .select('*')
          .eq('customerid', customerId)
          .order('createdon', { ascending: false });
        
        if (projectsError) {
          throw projectsError;
        }
        
        setProjects(projectsData || []);
      } catch (error: any) {
        console.error('Error fetching customer details:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (customerId) {
      fetchCustomerDetails();
    }
  }, [customerId]);
  
  function getStatusColor(status: string) {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
  
  function formatDate(dateString: string | null) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  }
  
  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      </AppLayout>
    );
  }
  
  if (error || !customer) {
    return (
      <AppLayout>
        <div className="bg-red-50 p-4 rounded-md">
          <div className="flex">
            <div>
              <p className="text-sm text-red-700">
                {error || 'Customer not found'}
              </p>
            </div>
          </div>
        </div>
        <div className="mt-4">
          <button
            type="button"
            onClick={() => router.push('/customers')}
            className="btn btn-outline"
          >
            Back to Customers
          </button>
        </div>
      </AppLayout>
    );
  }
  
  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{customer.customername}</h1>
          <p className="mt-2 text-sm text-gray-700">
            Customer ID: {customer.customerid}
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link
            href={`/customers/${customerId}/edit`}
            className="btn btn-primary mr-2"
          >
            Edit Customer
          </Link>
          <Link
            href="/customers"
            className="btn btn-outline"
          >
            Back to Customers
          </Link>
        </div>
      </div>
      
      <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Customer Information</h2>
          
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-3">
              <div className="text-sm font-medium text-gray-500">Status</div>
              <div className="mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(customer.status)}`}>
                  {customer.status}
                </span>
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <div className="text-sm font-medium text-gray-500">Created On</div>
              <div className="mt-1 text-sm text-gray-900">{formatDate(customer.createdon)}</div>
            </div>
            
            <div className="sm:col-span-4">
              <div className="text-sm font-medium text-gray-500">Address</div>
              <div className="mt-1 text-sm text-gray-900">
                {customer.address || 'N/A'}{customer.address ? ', ' : ''}
                {customer.city || ''}{customer.city ? ', ' : ''}
                {customer.state || ''} {customer.zip || ''}
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <div className="text-sm font-medium text-gray-500">Email</div>
              <div className="mt-1 text-sm text-gray-900">
                <a href={`mailto:${customer.contactemail}`} className="text-primary-600 hover:text-primary-500">
                  {customer.contactemail || 'N/A'}
                </a>
              </div>
            </div>
            
            <div className="sm:col-span-3">
              <div className="text-sm font-medium text-gray-500">Phone</div>
              <div className="mt-1 text-sm text-gray-900">
                <a href={customer.phone ? `tel:${customer.phone}` : '#'} className={`${customer.phone ? 'text-primary-600 hover:text-primary-500' : 'text-gray-900'}`}>
                  {customer.phone || 'N/A'}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mb-6">
        <div className="sm:flex sm:items-center sm:justify-between">
          <h2 className="text-lg font-medium text-gray-900">Customer Projects</h2>
          <Link
            href={`/projects/new?customerid=${customerId}`}
            className="mt-4 sm:mt-0 btn btn-primary-outline"
          >
            Add New Project
          </Link>
        </div>
      </div>
      
      {projects.length === 0 ? (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-6 text-center">
            <p className="text-gray-500">
              No projects found for this customer.
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Project ID
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Project Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Start Date
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Est. Cost
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {projects.map((project) => (
                <tr key={project.projectid}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {project.projectid}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {project.projectname}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                      {project.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(project.startdate)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${project.estimatedcost?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <Link
                      href={`/projects/${project.projectid}`}
                      className="text-primary-600 hover:text-primary-900 mr-4"
                    >
                      View
                    </Link>
                    <Link
                      href={`/projects/${project.projectid}/edit`}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      Edit
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppLayout>
  );
} 