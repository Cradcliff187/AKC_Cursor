"""
Database Service

This module provides services for interacting with the Supabase database.
"""

import os
from typing import Dict, Any, List, Optional, TypeVar, Generic, Type
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Type variable for generic database operations
T = TypeVar('T')

class DatabaseService:
    """Service for interacting with the Supabase database."""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of the database service exists."""
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Supabase client."""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and service role key must be set in environment variables.")
        
        self._client = create_client(supabase_url, supabase_key)
    
    @property
    def client(self) -> Client:
        """Get the Supabase client."""
        if self._client is None:
            self._initialize()
        return self._client
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a raw SQL query.
        
        Note: This method requires the exec_sql function to be created in Supabase.
        If you're getting errors, you may need to create this function manually in the Supabase SQL Editor.
        
        For most operations, it's better to use the standard Supabase client methods instead.
        """
        try:
            # Try to use exec_sql function if it exists
            try:
                response = self.client.rpc('exec_sql', {'query': query, 'params': params}).execute()
                return response.data
            except Exception as e:
                print(f"Error using exec_sql function: {str(e)}")
                print("Falling back to standard Supabase client methods.")
                
                # For simple SELECT queries, we can try to use the from_() method
                if query.strip().upper().startswith('SELECT'):
                    # Extract table name from query (this is a simplistic approach)
                    # In a real application, you would need a more robust SQL parser
                    table_match = query.lower().split('from')[1].strip().split()[0]
                    if table_match:
                        table_name = table_match.strip('"`[]')
                        response = self.client.table(table_name).select('*').execute()
                        return response.data
                
                # For other operations, we need to use the appropriate Supabase client methods
                # This would require parsing the SQL query and translating it to Supabase client methods
                # which is beyond the scope of this implementation
                raise NotImplementedError(
                    "Direct SQL execution without exec_sql is not fully implemented. "
                    "Please use the standard Supabase client methods or create the exec_sql function in Supabase."
                )
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            raise


class BaseModelService(Generic[T]):
    """Base service for model operations."""
    
    def __init__(self, table_name: str, model_class: Type[T]):
        """
        Initialize the base model service.
        
        Args:
            table_name: The name of the table in the database.
            model_class: The class of the model to use for this service.
        """
        self.db = DatabaseService()
        self.table_name = table_name
        self.model_class = model_class
    
    def create(self, data: Dict[str, Any]) -> Optional[T]:
        """
        Create a new record in the database.
        
        Args:
            data: The data to insert into the database.
            
        Returns:
            The created model instance, or None if creation failed.
        """
        try:
            # Generate a UUID if not provided
            if 'id' not in data:
                data['id'] = str(uuid.uuid4())
            
            # Add timestamps if not provided
            now = datetime.now().isoformat()
            if 'created_at' not in data:
                data['created_at'] = now
            if 'updated_at' not in data:
                data['updated_at'] = now
            
            # Insert the data into the database
            response = self.db.client.table(self.table_name).insert(data).execute()
            
            if response.data and len(response.data) > 0:
                # Return the created model instance
                return self.model_class.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error creating record in {self.table_name}: {str(e)}")
            return None
    
    def get(self, id: str) -> Optional[T]:
        """
        Get a record from the database by ID.
        
        Args:
            id: The ID of the record to get.
            
        Returns:
            The model instance, or None if not found.
        """
        try:
            response = self.db.client.table(self.table_name).select('*').eq('id', id).execute()
            
            if response.data and len(response.data) > 0:
                return self.model_class.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error getting record from {self.table_name}: {str(e)}")
            return None
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Update a record in the database.
        
        Args:
            id: The ID of the record to update.
            data: The data to update in the database.
            
        Returns:
            The updated model instance, or None if update failed.
        """
        try:
            # Add updated_at timestamp
            data['updated_at'] = datetime.now().isoformat()
            
            # Update the record in the database
            response = self.db.client.table(self.table_name).update(data).eq('id', id).execute()
            
            if response.data and len(response.data) > 0:
                return self.model_class.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"Error updating record in {self.table_name}: {str(e)}")
            return None
    
    def delete(self, id: str) -> bool:
        """
        Delete a record from the database.
        
        Args:
            id: The ID of the record to delete.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            response = self.db.client.table(self.table_name).delete().eq('id', id).execute()
            return response.data is not None
        except Exception as e:
            print(f"Error deleting record from {self.table_name}: {str(e)}")
            return False
    
    def list(self, filters: Dict[str, Any] = None, limit: int = 100, offset: int = 0) -> List[T]:
        """
        List records from the database with optional filtering.
        
        Args:
            filters: Optional dictionary of column-value pairs to filter by.
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            
        Returns:
            A list of model instances.
        """
        try:
            query = self.db.client.table(self.table_name).select('*').limit(limit).offset(offset)
            
            # Apply filters if provided
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)
            
            response = query.execute()
            
            if response.data:
                return [self.model_class.from_dict(item) for item in response.data]
            return []
        except Exception as e:
            print(f"Error listing records from {self.table_name}: {str(e)}")
            return [] 