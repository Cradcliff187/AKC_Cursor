from app.services.supabase import (
    get_table_data, insert_record, update_record, delete_record
)
from app.models.notification import Notification
from datetime import datetime
import json

def get_user_notifications(user_id, unread_only=False, limit=50):
    """Get notifications for a user"""
    filters = {'user_id': user_id}
    
    if unread_only:
        filters['is_read'] = False
    
    notification_data = get_table_data('notifications', filters=filters, limit=limit)
    
    # Convert to Notification objects
    notifications = [Notification.from_dict(n) for n in notification_data]
    
    # Sort by creation date, newest first
    notifications.sort(key=lambda n: n.created_at, reverse=True)
    
    return notifications

def get_notification_by_id(notification_id):
    """Get a notification by ID"""
    notification_data = get_table_data('notifications', filters={'id': notification_id})
    
    if notification_data and len(notification_data) > 0:
        return Notification.from_dict(notification_data[0])
    return None

def create_notification(notification_data):
    """Create a new notification"""
    # Create a Notification object to validate the data
    notification = Notification.from_dict(notification_data)
    
    # Insert the notification into the database
    result = insert_record('notifications', notification.to_dict())
    
    if result:
        return Notification.from_dict(result)
    return None

def update_notification(notification_id, notification_data):
    """Update a notification"""
    # Update the notification
    result = update_record('notifications', notification_id, notification_data)
    
    if result:
        return Notification.from_dict(result)
    return None

def mark_notification_as_read(notification_id):
    """Mark a notification as read"""
    return update_notification(notification_id, {'is_read': True})

def mark_all_notifications_as_read(user_id):
    """Mark all notifications for a user as read"""
    # This would typically be a batch update in the database
    # For now, we'll get all unread notifications and mark them as read one by one
    unread_notifications = get_user_notifications(user_id, unread_only=True)
    
    for notification in unread_notifications:
        mark_notification_as_read(notification.id)
    
    return True

def delete_notification(notification_id):
    """Delete a notification"""
    return delete_record('notifications', notification_id)

def get_unread_notification_count(user_id):
    """Get the count of unread notifications for a user"""
    unread_notifications = get_user_notifications(user_id, unread_only=True)
    return len(unread_notifications)

# Helper functions to generate common notifications

def notify_task_assignment(task, assignee_id):
    """Create a notification for a task assignment"""
    return create_notification({
        'user_id': assignee_id,
        'title': 'New Task Assignment',
        'message': f"You have been assigned to the task: {task.title}",
        'notification_type': 'info',
        'category': 'task',
        'entity_id': task.id,
        'entity_type': 'task',
        'action_url': f"/tasks/{task.id}"
    })

def notify_task_due_soon(task, user_id):
    """Create a notification for a task that's due soon"""
    return create_notification({
        'user_id': user_id,
        'title': 'Task Due Soon',
        'message': f"Task '{task.title}' is due in {task.days_remaining} days",
        'notification_type': 'warning',
        'category': 'task',
        'entity_id': task.id,
        'entity_type': 'task',
        'action_url': f"/tasks/{task.id}"
    })

def notify_task_overdue(task, user_id):
    """Create a notification for an overdue task"""
    return create_notification({
        'user_id': user_id,
        'title': 'Task Overdue',
        'message': f"Task '{task.title}' is now overdue",
        'notification_type': 'danger',
        'category': 'task',
        'entity_id': task.id,
        'entity_type': 'task',
        'action_url': f"/tasks/{task.id}"
    })

def notify_project_status_change(project, user_id, old_status):
    """Create a notification for a project status change"""
    return create_notification({
        'user_id': user_id,
        'title': 'Project Status Changed',
        'message': f"Project '{project.name}' status changed from {old_status} to {project.status}",
        'notification_type': 'info',
        'category': 'project',
        'entity_id': project.id,
        'entity_type': 'project',
        'action_url': f"/projects/{project.id}"
    })

def notify_document_upload(document, user_id):
    """Create a notification for a document upload"""
    return create_notification({
        'user_id': user_id,
        'title': 'New Document Uploaded',
        'message': f"A new document '{document.title}' has been uploaded",
        'notification_type': 'info',
        'category': 'document',
        'entity_id': document.id,
        'entity_type': 'document',
        'action_url': f"/documents/{document.id}"
    })

def notify_budget_warning(project, user_id):
    """Create a notification for a project nearing budget limit"""
    return create_notification({
        'user_id': user_id,
        'title': 'Budget Warning',
        'message': f"Project '{project.name}' has used {project.budget_percentage}% of its budget",
        'notification_type': 'warning',
        'category': 'project',
        'entity_id': project.id,
        'entity_type': 'project',
        'action_url': f"/projects/{project.id}/expenses"
    }) 