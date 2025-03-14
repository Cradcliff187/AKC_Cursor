"""
User Service

This module provides services for managing user profiles and notifications.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from models.user_profile import UserProfile, UserNotification, UserRole, UserStatus
from services.database_service import BaseModelService


class UserProfileService(BaseModelService[UserProfile]):
    """Service for managing user profiles."""
    
    def __init__(self):
        """Initialize the user profile service."""
        super().__init__('user_profiles', UserProfile)
    
    def get_by_auth_id(self, auth_id: str) -> Optional[UserProfile]:
        """
        Get a user profile by authentication ID.
        
        Args:
            auth_id: The authentication ID of the user.
            
        Returns:
            The user profile, or None if not found.
        """
        try:
            response = self.db.client.table(self.table_name).select('*').eq('auth_id', auth_id).execute()
            
            if response.data and len(response.data) > 0:
                return UserProfile.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error getting user profile by auth_id: {str(e)}")
            return None
    
    def get_by_email(self, email: str) -> Optional[UserProfile]:
        """
        Get a user profile by email.
        
        Args:
            email: The email of the user.
            
        Returns:
            The user profile, or None if not found.
        """
        try:
            response = self.db.client.table(self.table_name).select('*').eq('email', email).execute()
            
            if response.data and len(response.data) > 0:
                return UserProfile.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error getting user profile by email: {str(e)}")
            return None
    
    def list_by_role(self, role: UserRole) -> List[UserProfile]:
        """
        List user profiles by role.
        
        Args:
            role: The role to filter by.
            
        Returns:
            A list of user profiles with the specified role.
        """
        role_value = role.value if isinstance(role, UserRole) else role
        return self.list({'role': role_value})
    
    def list_by_status(self, status: UserStatus) -> List[UserProfile]:
        """
        List user profiles by status.
        
        Args:
            status: The status to filter by.
            
        Returns:
            A list of user profiles with the specified status.
        """
        status_value = status.value if isinstance(status, UserStatus) else status
        return self.list({'status': status_value})
    
    def list_by_department(self, department: str) -> List[UserProfile]:
        """
        List user profiles by department.
        
        Args:
            department: The department to filter by.
            
        Returns:
            A list of user profiles in the specified department.
        """
        return self.list({'department': department})
    
    def search(self, search_term: str) -> List[UserProfile]:
        """
        Search for user profiles by name or email.
        
        Args:
            search_term: The search term to look for.
            
        Returns:
            A list of user profiles matching the search term.
        """
        try:
            # Use Supabase's filter capabilities instead of raw SQL
            # This is more limited but doesn't require the exec_sql function
            search_pattern = f"%{search_term}%"
            
            # Search in email
            email_query = self.db.client.table(self.table_name).select('*').ilike('email', search_pattern)
            
            # Search in first_name
            first_name_query = self.db.client.table(self.table_name).select('*').ilike('first_name', search_pattern)
            
            # Search in last_name
            last_name_query = self.db.client.table(self.table_name).select('*').ilike('last_name', search_pattern)
            
            # Search in display_name
            display_name_query = self.db.client.table(self.table_name).select('*').ilike('display_name', search_pattern)
            
            # Execute all queries
            email_results = email_query.execute().data or []
            first_name_results = first_name_query.execute().data or []
            last_name_results = last_name_query.execute().data or []
            display_name_results = display_name_query.execute().data or []
            
            # Combine results and remove duplicates
            all_results = email_results + first_name_results + last_name_results + display_name_results
            unique_ids = set()
            unique_results = []
            
            for result in all_results:
                if result['id'] not in unique_ids:
                    unique_ids.add(result['id'])
                    unique_results.append(result)
            
            # Convert to UserProfile objects
            return [UserProfile.from_dict(item) for item in unique_results]
        except Exception as e:
            print(f"Error searching user profiles: {str(e)}")
            return []
    
    def update_last_login(self, user_id: str) -> Optional[UserProfile]:
        """
        Update the last login timestamp for a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            The updated user profile, or None if update failed.
        """
        try:
            data = {
                'last_login': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.db.client.table(self.table_name).update(data).eq('id', user_id).execute()
            
            if response.data and len(response.data) > 0:
                return UserProfile.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error updating last login: {str(e)}")
            return None


class UserNotificationService(BaseModelService[UserNotification]):
    """Service for managing user notifications."""
    
    def __init__(self):
        """Initialize the user notification service."""
        super().__init__('user_notifications', UserNotification)
    
    def list_for_user(self, user_id: str, include_read: bool = False) -> List[UserNotification]:
        """
        List notifications for a user.
        
        Args:
            user_id: The ID of the user.
            include_read: Whether to include read notifications.
            
        Returns:
            A list of notifications for the user.
        """
        try:
            query = self.db.client.table(self.table_name).select('*').eq('user_id', user_id)
            
            if not include_read:
                query = query.eq('is_read', False)
            
            response = query.order('created_at', desc=True).execute()
            
            if response.data:
                return [UserNotification.from_dict(item) for item in response.data]
            return []
        except Exception as e:
            print(f"Error listing notifications for user: {str(e)}")
            return []
    
    def mark_as_read(self, notification_id: str) -> Optional[UserNotification]:
        """
        Mark a notification as read.
        
        Args:
            notification_id: The ID of the notification.
            
        Returns:
            The updated notification, or None if update failed.
        """
        try:
            data = {
                'is_read': True,
                'read_at': datetime.now().isoformat()
            }
            
            response = self.db.client.table(self.table_name).update(data).eq('id', notification_id).execute()
            
            if response.data and len(response.data) > 0:
                return UserNotification.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error marking notification as read: {str(e)}")
            return None
    
    def mark_all_as_read(self, user_id: str) -> bool:
        """
        Mark all notifications for a user as read.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            data = {
                'is_read': True,
                'read_at': datetime.now().isoformat()
            }
            
            response = self.db.client.table(self.table_name).update(data).eq('user_id', user_id).eq('is_read', False).execute()
            
            return response.data is not None
        except Exception as e:
            print(f"Error marking all notifications as read: {str(e)}")
            return False
    
    def send_to_user(self, user_id: str, title: str, message: str, type: str = 'info', link: str = None) -> Optional[UserNotification]:
        """
        Send a notification to a user.
        
        Args:
            user_id: The ID of the user to send the notification to.
            title: The title of the notification.
            message: The message content of the notification.
            type: The type of notification (e.g., 'info', 'warning', 'error').
            link: A link associated with the notification.
            
        Returns:
            The created notification, or None if creation failed.
        """
        notification_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': type,
            'is_read': False,
            'link': link,
            'created_at': datetime.now().isoformat()
        }
        
        return self.create(notification_data)
    
    def send_to_role(self, role: UserRole, title: str, message: str, type: str = 'info', link: str = None) -> List[UserNotification]:
        """
        Send a notification to all users with a specific role.
        
        Args:
            role: The role to send notifications to.
            title: The title of the notification.
            message: The message content of the notification.
            type: The type of notification (e.g., 'info', 'warning', 'error').
            link: A link associated with the notification.
            
        Returns:
            A list of created notifications.
        """
        try:
            # Get all users with the specified role
            user_service = UserProfileService()
            users = user_service.list_by_role(role)
            
            notifications = []
            for user in users:
                notification = self.send_to_user(user.id, title, message, type, link)
                if notification:
                    notifications.append(notification)
            
            return notifications
        except Exception as e:
            print(f"Error sending notification to role: {str(e)}")
            return [] 