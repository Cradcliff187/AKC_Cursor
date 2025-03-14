"""
Document Model

This module defines the Document model and related functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class DocumentType(str, Enum):
    """Enum representing the possible document types."""
    CONTRACT = "contract"
    INVOICE = "invoice"
    BID = "bid"
    PERMIT = "permit"
    DRAWING = "drawing"
    SPECIFICATION = "specification"
    RECEIPT = "receipt"
    REPORT = "report"
    PHOTO = "photo"
    OTHER = "other"


class Document:
    """
    Represents a document in the system.
    
    Attributes:
        id (str): The unique identifier for the document.
        name (str): The name of the document.
        description (str): Description of the document.
        file_path (str): The path to the file in storage.
        file_type (str): The MIME type of the file.
        file_size (int): The size of the file in bytes.
        document_type (DocumentType): The type of document.
        project_id (str): The ID of the project this document is for (optional).
        client_id (str): The ID of the client this document is for (optional).
        invoice_id (str): The ID of the invoice this document is for (optional).
        bid_id (str): The ID of the bid this document is for (optional).
        tags (List[str]): Tags associated with the document.
        uploaded_by (str): The ID of the user who uploaded the document.
        version (int): The version number of the document.
        is_public (bool): Whether the document is publicly accessible.
        created_at (datetime): When the document was created.
        updated_at (datetime): When the document was last updated.
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        file_path: str,
        file_type: str,
        file_size: int,
        document_type: DocumentType = DocumentType.OTHER,
        description: str = None,
        project_id: str = None,
        client_id: str = None,
        invoice_id: str = None,
        bid_id: str = None,
        tags: List[str] = None,
        uploaded_by: str = None,
        version: int = 1,
        is_public: bool = False,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
        self.document_type = document_type if isinstance(document_type, DocumentType) else DocumentType(document_type)
        self.project_id = project_id
        self.client_id = client_id
        self.invoice_id = invoice_id
        self.bid_id = bid_id
        self.tags = tags or []
        self.uploaded_by = uploaded_by
        self.version = version
        self.is_public = is_public
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def file_extension(self) -> Optional[str]:
        """Get the file extension from the file path."""
        if not self.file_path:
            return None
        
        parts = self.file_path.split('.')
        if len(parts) > 1:
            return parts[-1].lower()
        return None
    
    @property
    def is_image(self) -> bool:
        """Check if the document is an image."""
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
        return self.file_type in image_types
    
    @property
    def is_pdf(self) -> bool:
        """Check if the document is a PDF."""
        return self.file_type == 'application/pdf'
    
    @property
    def file_size_formatted(self) -> str:
        """Get the file size in a human-readable format."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'document_type': self.document_type.value if isinstance(self.document_type, DocumentType) else self.document_type,
            'project_id': self.project_id,
            'client_id': self.client_id,
            'invoice_id': self.invoice_id,
            'bid_id': self.bid_id,
            'tags': self.tags,
            'uploaded_by': self.uploaded_by,
            'version': self.version,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create a document from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            file_path=data.get('file_path'),
            file_type=data.get('file_type'),
            file_size=data.get('file_size', 0),
            document_type=data.get('document_type', DocumentType.OTHER),
            project_id=data.get('project_id'),
            client_id=data.get('client_id'),
            invoice_id=data.get('invoice_id'),
            bid_id=data.get('bid_id'),
            tags=data.get('tags', []),
            uploaded_by=data.get('uploaded_by'),
            version=data.get('version', 1),
            is_public=data.get('is_public', False),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class DocumentVersion:
    """
    Represents a version of a document.
    
    Attributes:
        id (str): The unique identifier for the document version.
        document_id (str): The ID of the parent document.
        version_number (int): The version number.
        file_path (str): The path to the file in storage.
        file_size (int): The size of the file in bytes.
        uploaded_by (str): The ID of the user who uploaded this version.
        change_notes (str): Notes about what changed in this version.
        created_at (datetime): When this version was created.
    """
    
    def __init__(
        self,
        id: str,
        document_id: str,
        version_number: int,
        file_path: str,
        file_size: int,
        uploaded_by: str = None,
        change_notes: str = None,
        created_at: datetime = None
    ):
        self.id = id
        self.document_id = document_id
        self.version_number = version_number
        self.file_path = file_path
        self.file_size = file_size
        self.uploaded_by = uploaded_by
        self.change_notes = change_notes
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the document version to a dictionary."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'version_number': self.version_number,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'uploaded_by': self.uploaded_by,
            'change_notes': self.change_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentVersion':
        """Create a document version from a dictionary."""
        return cls(
            id=data.get('id'),
            document_id=data.get('document_id'),
            version_number=data.get('version_number', 1),
            file_path=data.get('file_path'),
            file_size=data.get('file_size', 0),
            uploaded_by=data.get('uploaded_by'),
            change_notes=data.get('change_notes'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None
        )


class DocumentService:
    """Service for managing documents and document versions."""
    
    @staticmethod
    def create_document(document_data: Dict[str, Any], file) -> Document:
        """Create a new document."""
        # Implementation would depend on your database access layer and file storage system
        pass
    
    @staticmethod
    def get_document(document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_document(document_id: str, document_data: Dict[str, Any]) -> Optional[Document]:
        """Update an existing document."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_document(document_id: str) -> bool:
        """Delete a document."""
        # Implementation would depend on your database access layer and file storage system
        pass
    
    @staticmethod
    def list_documents(
        project_id: str = None,
        client_id: str = None,
        invoice_id: str = None,
        bid_id: str = None,
        document_type: str = None,
        tags: List[str] = None,
        uploaded_by: str = None
    ) -> List[Document]:
        """List documents with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def upload_new_version(document_id: str, file, change_notes: str = None) -> Optional[Document]:
        """Upload a new version of a document."""
        # Implementation would depend on your database access layer and file storage system
        pass
    
    @staticmethod
    def get_document_versions(document_id: str) -> List[DocumentVersion]:
        """Get all versions of a document."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_document_version(document_id: str, version_number: int) -> Optional[DocumentVersion]:
        """Get a specific version of a document."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def search_documents(search_term: str) -> List[Document]:
        """Search for documents by name, description, or tags."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def generate_download_url(document_id: str, version_number: int = None) -> Optional[str]:
        """Generate a download URL for a document."""
        # Implementation would depend on your file storage system
        pass 