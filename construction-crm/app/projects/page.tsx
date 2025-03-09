'use client';

import React, { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { Project } from '@/lib/supabase';
import { PROJECT_STATUSES } from '@/lib/constants';
import { formatDate } from '@/lib/utils';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const router = useRouter();

  useEffect(() => {
    fetchProjects();
  }, [statusFilter]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      
      let query = supabase
        .from('projects')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (statusFilter !== 'all') {
        query = query.eq('status', statusFilter);
      }
      
      const { data, error } = await query;
      
      if (error) {
        throw error;
      }
      
      setProjects(data || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Filter projects client-side for the search
    // A more robust solution would search on the server
  };

  const filteredProjects = projects.filter(project => {
    const projectNameMatch = project.projectname?.toLowerCase().includes(searchQuery.toLowerCase());
    const customerNameMatch = project.customername?.toLowerCase().includes(searchQuery.toLowerCase());
    const jobDescMatch = project.jobdescription?.toLowerCase().includes(searchQuery.toLowerCase());
    
    return projectNameMatch || customerNameMatch || jobDescMatch;
  });

  const getStatusColor = (status: string): string => {
    switch (status) {
      case PROJECT_STATUSES.PENDING:
        return 'bg-yellow-100 text-yellow-800';
      case PROJECT_STATUSES.APPROVED:
        return 'bg-blue-100 text-blue-800';
      case PROJECT_STATUSES.IN_PROGRESS:
        return 'bg-green-100 text-green-800';
      case PROJECT_STATUSES.COMPLETED:
        return 'bg-purple-100 text-purple-800';
      case PROJECT_STATUSES.CANCELED:
        return 'bg-red-100 text-red-800';
      case PROJECT_STATUSES.CLOSED:
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <AppLayout>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all projects in your account.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link href="/projects/new" className="btn btn-primary">
            New Project
          </Link>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 border-b border-gray-200 sm:flex sm:items-center sm:justify-between">
          <form onSubmit={handleSearch} className="sm:flex-1 sm:flex sm:items-center">
            <div className="sm:w-64">
              <label htmlFor="search" className="sr-only">
                Search projects
              </label>
              <input
                type="text"
                id="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search projects..."
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
              <option value={PROJECT_STATUSES.PENDING}>{PROJECT_STATUSES.PENDING}</option>
              <option value={PROJECT_STATUSES.APPROVED}>{PROJECT_STATUSES.APPROVED}</option>
              <option value={PROJECT_STATUSES.IN_PROGRESS}>{PROJECT_STATUSES.IN_PROGRESS}</option>
              <option value={PROJECT_STATUSES.COMPLETED}>{PROJECT_STATUSES.COMPLETED}</option>
              <option value={PROJECT_STATUSES.CANCELED}>{PROJECT_STATUSES.CANCELED}</option>
              <option value={PROJECT_STATUSES.CLOSED}>{PROJECT_STATUSES.CLOSED}</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="p-4 text-center">
            <p className="text-gray-500">Loading projects...</p>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="p-4 text-center">
            <p className="text-gray-500">No projects found.</p>
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
                    Project ID
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Project
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredProjects.map((project) => (
                  <tr 
                    key={project.projectid} 
                    onClick={() => router.push(`/projects/${project.projectid}`)}
                    className="cursor-pointer hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {project.projectid}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{project.projectname}</div>
                          <div className="text-sm text-gray-500">{project.jobdescription ? `${project.jobdescription.substring(0, 50)}${project.jobdescription.length > 50 ? '...' : ''}` : 'No description'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{project.customername || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {[project.sitelocationcity, project.sitelocationstate].filter(Boolean).join(', ') || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(project.status || '')}`}>
                        {project.status || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {project.created_at ? formatDate(project.created_at) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div onClick={(e) => e.stopPropagation()} className="flex space-x-2 justify-end">
                        <Link 
                          href={`/projects/${project.projectid}`} 
                          className="text-primary-600 hover:text-primary-900"
                        >
                          View
                        </Link>
                        <Link 
                          href={`/projects/${project.projectid}/edit`} 
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