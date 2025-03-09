'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import Link from 'next/link';

type TimeLog = {
  timeid: string;
  projectid: string;
  employeeid: string;
  hours: number;
  entrydate: string;
  description: string;
  hourlyrate: number;
  totalamount: number;
  createdon: string;
  createdby: string;
  employee: {
    firstname: string;
    lastname: string;
  };
};

type Project = {
  projectid: string;
  projectname: string;
};

export default function TimeLogsPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.projectId as string;
  
  const [timeLogs, setTimeLogs] = useState<TimeLog[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [employeeFilter, setEmployeeFilter] = useState<string>('');
  const [employees, setEmployees] = useState<{ employeeid: string, name: string }[]>([]);
  
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
        
        // Fetch time logs with employee information
        const { data: timeLogsData, error: timeLogsError } = await supabase
          .from('timelogs')
          .select(`
            *,
            employee:employeeid (
              firstname,
              lastname
            )
          `)
          .eq('projectid', projectId)
          .order('entrydate', { ascending: false });
        
        if (timeLogsError) {
          throw timeLogsError;
        }
        
        setTimeLogs(timeLogsData || []);
        
        // Extract unique employees for filter dropdown
        const uniqueEmployees = Array.from(
          new Set(timeLogsData?.map(log => log.employeeid))
        ).map(employeeId => {
          const log = timeLogsData?.find(l => l.employeeid === employeeId);
          return {
            employeeid: employeeId as string,
            name: `${log?.employee?.lastname}, ${log?.employee?.firstname}`
          };
        });
        
        setEmployees(uniqueEmployees);
      } catch (error: any) {
        console.error('Error fetching time logs:', error);
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
  
  const filterTimeLogs = () => {
    return timeLogs.filter(log => {
      // Apply date filter if both start and end dates are provided
      const dateMatch = startDate && endDate
        ? new Date(log.entrydate) >= new Date(startDate) && new Date(log.entrydate) <= new Date(endDate)
        : true;
      
      // Apply employee filter if selected
      const employeeMatch = employeeFilter
        ? log.employeeid === employeeFilter
        : true;
      
      return dateMatch && employeeMatch;
    });
  };
  
  const clearFilters = () => {
    setStartDate('');
    setEndDate('');
    setEmployeeFilter('');
  };
  
  const calculateTotalHours = (logs: TimeLog[]) => {
    return logs.reduce((total, log) => total + log.hours, 0);
  };
  
  const calculateTotalAmount = (logs: TimeLog[]) => {
    return logs.reduce((total, log) => total + log.totalamount, 0);
  };
  
  const filteredLogs = filterTimeLogs();
  
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
          <h1 className="text-3xl font-bold text-gray-900">Time Logs</h1>
          <p className="mt-2 text-sm text-gray-700">
            Project: {project.projectname}
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <Link
            href={`/projects/${projectId}/time/new`}
            className="btn btn-primary"
          >
            Add Time Log
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
          <h2 className="text-lg font-medium text-gray-900 mb-4">Filter Time Logs</h2>
          
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
              <label htmlFor="employeeFilter" className="block text-sm font-medium text-gray-700">
                Employee
              </label>
              <div className="mt-1">
                <select
                  id="employeeFilter"
                  value={employeeFilter}
                  onChange={(e) => setEmployeeFilter(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">All Employees</option>
                  {employees.map((employee) => (
                    <option key={employee.employeeid} value={employee.employeeid}>
                      {employee.name}
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
      
      {filteredLogs.length === 0 ? (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-6 text-center">
            <p className="text-gray-500">
              No time logs found for this project.
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Summary</h2>
              
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-500">Total Hours</p>
                  <p className="mt-1 text-3xl font-semibold text-gray-900">
                    {calculateTotalHours(filteredLogs).toFixed(2)}
                  </p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-500">Total Amount</p>
                  <p className="mt-1 text-3xl font-semibold text-gray-900">
                    {formatCurrency(calculateTotalAmount(filteredLogs))}
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
                    Employee
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Hours
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rate
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLogs.map((log) => (
                  <tr key={log.timeid}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatDate(log.entrydate)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.employee ? `${log.employee.lastname}, ${log.employee.firstname}` : 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.hours.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(log.hourlyrate)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(log.totalamount)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">
                      {log.description}
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