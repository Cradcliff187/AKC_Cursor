'use client';

import React, { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { Customer } from '@/lib/supabase';
import { CUSTOMER_STATUSES } from '@/lib/constants';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const router = useRouter();

  useEffect(() => {
    fetchCustomers();
  }, [statusFilter]);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      
      let query = supabase
        .from('customers')
        .select('*')
        .order('customername', { ascending: true });
      
      if (statusFilter !== 'all') {
        query = query.eq('status', statusFilter);
      }
      
      const { data, error } = await query;
      
      if (error) {
        throw error;
      }
      
      setCustomers(data || []);
    } catch (error) {
      console.error('Error fetching customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Filter customers client-side for the search
    // A more robust solution would search on the server
  };

  const filteredCustomers = customers.filter(customer => {
    const customerNameMatch = customer.customername?.toLowerCase().includes(searchQuery.toLowerCase());
    const emailMatch = customer.contactemail?.toLowerCase().includes(searchQuery.toLowerCase());
    const phoneMatch = customer.phone?.toLowerCase().includes(searchQuery.toLowerCase());
    const addressMatch = customer.address?.toLowerCase().includes(searchQuery.toLowerCase());
    
    return customerNameMatch || emailMatch || phoneMatch || addressMatch;
  });

  const getStatusColor = (status: string): string => {
    switch (status) {
      case CUSTOMER_STATUSES.ACTIVE:
        return 'bg-green-100 text-green-800';
      case CUSTOMER_STATUSES.INACTIVE:
        return 'bg-gray-100 text-gray-800';
      case CUSTOMER_STATUSES.PENDING:
        return 'bg-yellow-100 text-yellow-800';
      case CUSTOMER_STATUSES.ARCHIVED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all customers in your account.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link href="/customers/new" className="btn btn-primary">
            New Customer
          </Link>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 border-b border-gray-200 sm:flex sm:items-center sm:justify-between">
          <form onSubmit={handleSearch} className="sm:flex-1 sm:flex sm:items-center">
            <div className="sm:w-64">
              <label htmlFor="search" className="sr-only">
                Search customers
              </label>
              <input
                type="text"
                id="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search customers..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </div>
            <div className="mt-2 sm:mt-0 sm:ml-4">
              <button type="submit" className="btn btn-outline sm:w-auto w-full">
                Search
              </button>
            </div>
          </form>
          <div className="mt-3 sm:mt-0 sm:ml-4">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="all">All Statuses</option>
              <option value={CUSTOMER_STATUSES.ACTIVE}>{CUSTOMER_STATUSES.ACTIVE}</option>
              <option value={CUSTOMER_STATUSES.INACTIVE}>{CUSTOMER_STATUSES.INACTIVE}</option>
              <option value={CUSTOMER_STATUSES.PENDING}>{CUSTOMER_STATUSES.PENDING}</option>
              <option value={CUSTOMER_STATUSES.ARCHIVED}>{CUSTOMER_STATUSES.ARCHIVED}</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="p-4 text-center">
            <p className="text-gray-500">Loading customers...</p>
          </div>
        ) : filteredCustomers.length === 0 ? (
          <div className="p-4 text-center">
            <p className="text-gray-500">No customers found.</p>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="mt-2 text-primary-600 hover:text-primary-800"
              >
                Clear search
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCustomers.map((customer) => (
                  <tr 
                    key={customer.customerid} 
                    onClick={() => router.push(`/customers/${customer.customerid}`)}
                    className="cursor-pointer hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{customer.customername}</div>
                          <div className="text-sm text-gray-500">ID: {customer.customerid}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{customer.contactemail || 'N/A'}</div>
                      <div className="text-sm text-gray-500">{customer.phone || 'No phone'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {[customer.city, customer.state].filter(Boolean).join(', ') || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(customer.status || '')}`}>
                        {customer.status || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div onClick={(e) => e.stopPropagation()} className="flex space-x-2 justify-end">
                        <Link 
                          href={`/customers/${customer.customerid}`} 
                          className="text-primary-600 hover:text-primary-900"
                        >
                          View
                        </Link>
                        <Link 
                          href={`/customers/${customer.customerid}/edit`} 
                          className="text-gray-600 hover:text-gray-900"
                        >
                          Edit
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppLayout>
  );
} 