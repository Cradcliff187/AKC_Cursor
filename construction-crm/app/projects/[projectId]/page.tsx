'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import AppLayout from '@/components/layout/AppLayout';
import Link from 'next/link';
import { Project, TimeLog, MaterialsReceipt, SubInvoice, Estimate } from '@/lib/supabase';
import { PROJECT_STATUSES, STATUS_TRANSITIONS } from '@/lib/constants';
import { formatDate, formatCurrency, isStatusTransitionAllowed, generateActivityLogId } from '@/lib/utils';

type ProjectDetailProps = {
  params: {
    projectId: string;
  };
};

export default function ProjectDetailPage({ params }: ProjectDetailProps) {
  const { projectId } = params;
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [timeLogs, setTimeLogs] = useState<TimeLog[]>([]);
  const [materialsReceipts, setMaterialsReceipts] = useState<MaterialsReceipt[]>([]);
  const [subInvoices, setSubInvoices] = useState<SubInvoice[]>([]);
  const [estimates, setEstimates] = useState<Estimate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [newStatus, setNewStatus] = useState<string | null>(null);
  const [statusUpdateLoading, setStatusUpdateLoading] = useState(false);

  // Fetch all project data
  useEffect(() => {
    const fetchProjectData = async () => {
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
        
        if (projectData) {
          // Fetch time logs
          const { data: timeLogsData, error: timeLogsError } = await supabase
            .from('timelogs')
            .select('*')
            .eq('projectid', projectId)
            .order('dateworked', { ascending: false });
            
          if (timeLogsError) throw timeLogsError;
          setTimeLogs(timeLogsData || []);
          
          // Fetch materials receipts
          const { data: materialsData, error: materialsError } = await supabase
            .from('materialsreceipts')
            .select('*')
            .eq('projectid', projectId)
            .order('created_at', { ascending: false });
            
          if (materialsError) throw materialsError;
          setMaterialsReceipts(materialsData || []);
          
          // Fetch subcontractor invoices
          const { data: subInvoicesData, error: subInvoicesError } = await supabase
            .from('subinvoices')
            .select('*')
            .eq('projectid', projectId)
            .order('created_at', { ascending: false });
            
          if (subInvoicesError) throw subInvoicesError;
          setSubInvoices(subInvoicesData || []);
          
          // Fetch estimates
          const { data: estimatesData, error: estimatesError } = await supabase
            .from('estimates')
            .select('*')
            .eq('projectid', projectId)
            .order('created_at', { ascending: false });
            
          if (estimatesError) throw estimatesError;
          setEstimates(estimatesData || []);
        }
      } catch (error: any) {
        console.error('Error fetching project data:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProjectData();
  }, [projectId]);

  const getAvailableStatusTransitions = () => {
    if (!project || !project.status) return [];
    
    // Get allowed next statuses based on current status
    const transitions = STATUS_TRANSITIONS.PROJECT[project.status] || [];
    return transitions;
  };

  const handleStatusChange = async () => {
    if (!project || !newStatus) return;
    
    try {
      setStatusUpdateLoading(true);
      
      // Check if transition is allowed
      if (!isStatusTransitionAllowed('PROJECT', project.status || '', newStatus)) {
        throw new Error(`Status transition from ${project.status} to ${newStatus} is not allowed`);
      }
      
      const previousStatus = project.status;
      
      // Update project status
      const { error: updateError } = await supabase
        .from('projects')
        .update({ 
          status: newStatus,
          lastmodified: new Date().toISOString(),
          lastmodifiedby: (await supabase.auth.getUser()).data.user?.email || 'Unknown'
        })
        .eq('projectid', projectId);
        
      if (updateError) throw updateError;
      
      // Log the status change in activity log
      const { error: logError } = await supabase
        .from('activitylog')
        .insert({
          logid: generateActivityLogId(),
          timestamp: new Date().toISOString(),
          action: 'Status Changed',
          useremail: (await supabase.auth.getUser()).data.user?.email,
          moduletype: 'Projects',
          referenceid: projectId,
          status: newStatus,
          previousstatus: previousStatus,
          detailsjson: JSON.stringify({
            projectId,
            newStatus,
            previousStatus
          })
        });
        
      if (logError) throw logError;
      
      // Update local state
      setProject({
        ...project,
        status: newStatus,
        lastmodified: new Date().toISOString()
      });
      
      setShowStatusModal(false);
    } catch (error: any) {
      console.error('Error updating status:', error);
      setError(error.message);
    } finally {
      setStatusUpdateLoading(false);
    }
  };

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

  const getTotalTimeHours = () => {
    return timeLogs.reduce((total, log) => {
      const hours = parseFloat(log.totalhours || '0');
      return isNaN(hours) ? total : total + hours;
    }, 0);
  };

  const getTotalMaterialsCost = () => {
    return materialsReceipts.reduce((total, receipt) => {
      return total + (receipt.amount || 0);
    }, 0);
  };

  const getTotalSubcontractorCost = () => {
    return subInvoices.reduce((total, invoice) => {
      return total + (invoice.invoiceamount || 0);
    }, 0);
  };

  const getProjectTotal = () => {
    // Combine materials and subcontractor costs
    return getTotalMaterialsCost() + getTotalSubcontractorCost();
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

  if (error) {
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

  if (!project) {
    return (
      <AppLayout>
        <div className="bg-yellow-50 p-4 rounded-md mb-4">
          <div className="flex">
            <div>
              <h3 className="text-sm font-medium text-yellow-800">Project Not Found</h3>
              <p className="text-sm text-yellow-700 mt-2">The project you're looking for doesn't exist or you don't have access to it.</p>
              <button
                onClick={() => router.push('/projects')}
                className="mt-4 bg-white text-sm text-yellow-600 px-4 py-2 border border-yellow-300 rounded-md shadow-sm hover:bg-yellow-50"
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
      {/* Header with back button and actions */}
      <div className="mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div className="flex items-center">
            <button
              onClick={() => router.push('/projects')}
              className="mr-4 text-gray-500 hover:text-gray-700"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{project.projectname}</h1>
              <p className="text-sm text-gray-500">Project ID: {project.projectid}</p>
            </div>
          </div>
          <div className="mt-4 md:mt-0 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
            <Link href={`/projects/${projectId}/edit`} className="btn btn-outline">
              Edit Project
            </Link>
            <button
              onClick={() => {
                setNewStatus(null);
                setShowStatusModal(true);
              }}
              className="btn btn-primary"
            >
              Change Status
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project Details - Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Project Information */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Project Details</h3>
            </div>
            <div className="px-4 py-5 sm:p-6">
              <div className="flex flex-wrap -mx-2">
                <div className="px-2 w-full md:w-1/2 mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Status</div>
                  <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(project.status || '')}`}>
                    {project.status || 'Unknown'}
                  </span>
                </div>
                <div className="px-2 w-full md:w-1/2 mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Customer</div>
                  <div className="text-sm text-gray-900">
                    {project.customername ? (
                      <Link href={`/customers/${project.customerid}`} className="text-primary-600 hover:text-primary-900">
                        {project.customername}
                      </Link>
                    ) : (
                      'N/A'
                    )}
                  </div>
                </div>
                <div className="px-2 w-full md:w-1/2 mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Created On</div>
                  <div className="text-sm text-gray-900">{project.createdon ? formatDate(project.createdon) : 'N/A'}</div>
                </div>
                <div className="px-2 w-full md:w-1/2 mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Created By</div>
                  <div className="text-sm text-gray-900">{project.createdby || 'N/A'}</div>
                </div>
                <div className="px-2 w-full md:w-1/2 mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Last Modified</div>
                  <div className="text-sm text-gray-900">{project.lastmodified ? formatDate(project.lastmodified) : 'N/A'}</div>
                </div>
                <div className="px-2 w-full md:w-1/2 mb-4">
                  <div className="text-sm font-medium text-gray-500 mb-1">Last Modified By</div>
                  <div className="text-sm text-gray-900">{project.lastmodifiedby || 'N/A'}</div>
                </div>
              </div>

              {/* Job Description */}
              <div className="mt-4">
                <div className="text-sm font-medium text-gray-500 mb-1">Job Description</div>
                <div className="mt-1 text-sm text-gray-900 bg-gray-50 p-3 rounded">
                  {project.jobdescription || 'No description provided.'}
                </div>
              </div>

              {/* Site Location */}
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-500 mb-3">Site Location</h4>
                <div className="bg-gray-50 p-3 rounded text-sm">
                  {project.sitelocationaddress && (
                    <div className="mb-1">{project.sitelocationaddress}</div>
                  )}
                  {(project.sitelocationcity || project.sitelocationstate || project.sitelocationzip) && (
                    <div>
                      {[
                        project.sitelocationcity,
                        project.sitelocationstate,
                        project.sitelocationzip
                      ]
                        .filter(Boolean)
                        .join(', ')}
                    </div>
                  )}
                  {!project.sitelocationaddress &&
                    !project.sitelocationcity &&
                    !project.sitelocationstate &&
                    !project.sitelocationzip && (
                      <div className="text-gray-500">No location information provided.</div>
                    )}
                </div>
              </div>
            </div>
          </div>

          {/* Tabs for Time Logs, Materials, and Invoices */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex">
                <button
                  className="w-1/3 py-4 px-1 text-center border-b-2 border-primary-500 font-medium text-sm text-primary-600"
                >
                  Time Logs ({timeLogs.length})
                </button>
                <button
                  className="w-1/3 py-4 px-1 text-center border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
                >
                  Materials ({materialsReceipts.length})
                </button>
                <button
                  className="w-1/3 py-4 px-1 text-center border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
                >
                  Subcontractor Invoices ({subInvoices.length})
                </button>
              </nav>
            </div>

            {/* Time Logs Content */}
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Time Logs</h3>
                <Link
                  href={`/projects/${projectId}/timelogs/new`}
                  className="btn btn-primary text-sm"
                >
                  Add Time Log
                </Link>
              </div>

              {timeLogs.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-sm text-gray-500">No time logs recorded for this project.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          User
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Hours
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Time
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {timeLogs.map((log) => (
                        <tr key={log.timelogid}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {log.dateworked ? formatDate(log.dateworked) : 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.submittinguser || log.foruseremail || 'Unknown'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {log.totalhours || '0'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.starttime && log.endtime
                              ? `${log.starttime} - ${log.endtime}`
                              : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Summaries and Links */}
        <div className="space-y-6">
          {/* Project Financials Summary */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Project Summary</h3>
            </div>
            <div className="px-4 py-5 sm:p-6 space-y-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <div className="text-sm font-medium text-gray-500">Total Hours</div>
                  <div className="text-sm font-semibold text-gray-900">{getTotalTimeHours()}</div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-500 h-2 rounded-full" style={{ width: `${Math.min(getTotalTimeHours() / 100 * 100, 100)}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <div className="text-sm font-medium text-gray-500">Materials Cost</div>
                  <div className="text-sm font-semibold text-gray-900">{formatCurrency(getTotalMaterialsCost())}</div>
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <div className="text-sm font-medium text-gray-500">Subcontractor Cost</div>
                  <div className="text-sm font-semibold text-gray-900">{formatCurrency(getTotalSubcontractorCost())}</div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <div className="text-base font-medium text-gray-900">Project Total</div>
                  <div className="text-base font-bold text-gray-900">{formatCurrency(getProjectTotal())}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Estimates List */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Estimates</h3>
            </div>
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <div className="text-sm text-gray-500">{estimates.length} estimate(s)</div>
                <Link href={`/projects/${projectId}/estimates/new`} className="text-sm text-primary-600 hover:text-primary-800">
                  Create Estimate
                </Link>
              </div>

              {estimates.length === 0 ? (
                <div className="text-center py-4">
                  <p className="text-sm text-gray-500">No estimates created for this project.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {estimates.map((estimate) => (
                    <div key={estimate.estimateid} className="border border-gray-200 rounded-md p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{estimate.estimateid}</div>
                          <div className="text-xs text-gray-500">
                            {estimate.datecreated ? formatDate(estimate.datecreated) : 'N/A'}
                          </div>
                        </div>
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          estimate.status === 'Approved' ? 'bg-green-100 text-green-800' :
                          estimate.status === 'Rejected' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {estimate.status || 'Pending'}
                        </span>
                      </div>
                      <div className="mt-2 flex justify-between">
                        <div className="text-sm font-medium text-gray-900">{formatCurrency(estimate.estimateamount || 0)}</div>
                        <Link href={`/projects/${projectId}/estimates/${estimate.estimateid}`} className="text-xs text-primary-600 hover:text-primary-800">
                          View Details
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quick Links */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Quick Actions</h3>
            </div>
            <div className="px-4 py-5 sm:p-6">
              <div className="space-y-3">
                <Link href={`/projects/${projectId}/timelogs/new`} className="block w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded text-sm text-gray-700">
                  Add Time Log
                </Link>
                <Link href={`/projects/${projectId}/materials/new`} className="block w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded text-sm text-gray-700">
                  Add Materials Receipt
                </Link>
                <Link href={`/projects/${projectId}/subinvoices/new`} className="block w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded text-sm text-gray-700">
                  Add Subcontractor Invoice
                </Link>
                <Link href={`/projects/${projectId}/estimates/new`} className="block w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded text-sm text-gray-700">
                  Create Estimate
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Change Modal */}
      {showStatusModal && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
          <div className="bg-white rounded-lg max-w-md w-full mx-4">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Change Project Status</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Status
                </label>
                <div className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(project.status || '')}`}>
                  {project.status || 'Unknown'}
                </div>
              </div>

              <div className="mb-4">
                <label htmlFor="newStatus" className="block text-sm font-medium text-gray-700 mb-2">
                  New Status
                </label>
                <select
                  id="newStatus"
                  value={newStatus || ''}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">Select new status</option>
                  {getAvailableStatusTransitions().map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
                {getAvailableStatusTransitions().length === 0 && (
                  <p className="mt-2 text-sm text-red-600">
                    No status transitions available from current status.
                  </p>
                )}
              </div>

              <div className="mt-5 sm:mt-6 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowStatusModal(false)}
                  className="btn btn-outline"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleStatusChange}
                  disabled={!newStatus || statusUpdateLoading}
                  className="btn btn-primary"
                >
                  {statusUpdateLoading ? 'Updating...' : 'Change Status'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
} 