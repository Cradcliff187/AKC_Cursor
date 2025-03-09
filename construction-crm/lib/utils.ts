/**
 * Utility functions for the Construction CRM
 */

import { v4 as uuidv4 } from 'uuid';
import { ID_PATTERNS, STATUS_TRANSITIONS, MODULE_ACCESS } from './constants';

/**
 * Generate a unique project ID following the pattern PROJ-YYMM-XXX
 * @param sequence Optional sequence number (will be auto-incremented if not provided)
 */
export const generateProjectId = (): string => {
  return `PRJ-${uuidv4().substring(0, 8)}`;
};

/**
 * Generate a unique customer ID following the pattern YY-XXX
 * @param sequence Optional sequence number (will be auto-incremented if not provided)
 */
export const generateCustomerId = (sequenceNumber: number): string => {
  const year = new Date().getFullYear().toString().slice(-2);
  return `${year}-${sequenceNumber.toString().padStart(4, '0')}`;
};

/**
 * Generate a unique subcontractor ID following the pattern SUB-XXX
 * @param sequence Optional sequence number (will be auto-incremented if not provided)
 */
export const generateSubcontractorId = (sequence?: number): string => {
  const seq = sequence ? sequence.toString().padStart(3, '0') : '001';
  
  return `SUB-${seq}`;
};

/**
 * Generate a unique vendor ID following the pattern VEND-XXX
 * @param sequence Optional sequence number (will be auto-incremented if not provided)
 */
export const generateVendorId = (sequence?: number): string => {
  const seq = sequence ? sequence.toString().padStart(3, '0') : '001';
  
  return `VEND-${seq}`;
};

/**
 * Generate a unique estimate ID following the pattern EST-ProjectID-X
 * @param projectId The ID of the project this estimate belongs to
 * @param version The version number of this estimate
 */
export const generateEstimateId = (projectId: string, version: number = 1): string => {
  return `EST-${projectId}-${version}`;
};

/**
 * Generate a unique time entry ID with timestamp
 */
export const generateTimeEntryId = (): string => {
  const timestamp = Date.now().toString();
  return `TL${timestamp}`;
};

/**
 * Generate a unique materials receipt ID with timestamp
 */
export const generateMaterialsReceiptId = (): string => {
  const timestamp = Date.now().toString();
  return `MATREC-${timestamp}`;
};

/**
 * Generate a unique subcontractor invoice ID with timestamp
 */
export const generateSubInvoiceId = (): string => {
  const timestamp = Date.now().toString();
  return `SUBINV-${timestamp}`;
};

/**
 * Generate a unique activity log ID with timestamp
 */
export const generateActivityLogId = (): string => {
  const timestamp = Date.now().toString();
  return `LOG-${timestamp}`;
};

/**
 * Generate a project folder name following the pattern {CustomerID}-{ProjectID}-{ProjectName}
 */
export const generateProjectFolderName = (customerId: string, projectId: string, projectName: string): string => {
  // Replace spaces and special characters with underscores for safe folder names
  const safeName = projectName.replace(/[^a-zA-Z0-9]/g, '_');
  return `${customerId}-${projectId}-${safeName}`;
};

/**
 * Check if a status transition is allowed
 * @param entityType The type of entity (PROJECT or ESTIMATE)
 * @param currentStatus The current status
 * @param newStatus The proposed new status
 * @returns boolean indicating if the transition is allowed
 */
export const isStatusTransitionAllowed = (
  entityType: 'PROJECT' | 'ESTIMATE',
  currentStatus: string,
  newStatus: string
): boolean => {
  if (!STATUS_TRANSITIONS[entityType] || !STATUS_TRANSITIONS[entityType][currentStatus]) {
    return false;
  }
  
  return STATUS_TRANSITIONS[entityType][currentStatus].includes(newStatus);
};

/**
 * Check if a specific module is accessible based on project status
 * @param moduleName The module to check access for
 * @param projectStatus The current status of the project
 * @returns boolean indicating if the module is accessible
 */
export const isModuleAccessible = (moduleName: string, projectStatus: string): boolean => {
  if (!MODULE_ACCESS[moduleName]) {
    return false;
  }
  
  return MODULE_ACCESS[moduleName].includes(projectStatus);
};

/**
 * Format a currency value
 * @param amount The amount to format
 * @returns Formatted currency string
 */
export const formatCurrency = (amount: number): string => {
  return amount.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  });
};

/**
 * Format a date
 * @param dateString The date string to format
 * @returns Formatted date string
 */
export const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString();
}; 