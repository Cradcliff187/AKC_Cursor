from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import shutil
import logging
import traceback
from pathlib import Path
from dependencies import get_session, check_auth, get_supabase_client, templates
from routes.auth import require_auth

router = APIRouter(prefix="/documents", tags=["documents"])

# Configure upload directory
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mock document data
MOCK_DOCUMENTS = [
    {
        "id": 1,
        "filename": "contract_123.pdf",
        "file_path": "/static/uploads/contract_123.pdf", 
        "document_type": "contract",
        "description": "Service agreement with client",
        "project_id": 1,
        "vendor_id": None,
        "uploaded_by": "admin",
        "uploaded_at": "2025-03-14T10:00:00Z",
        "file_size": 1024000,
        "mime_type": "application/pdf"
    },
    {
        "id": 2,
        "filename": "invoice_abc123.pdf",
        "file_path": "/static/uploads/invoice_abc123.pdf",
        "document_type": "invoice",
        "description": "Monthly invoice from vendor",
        "project_id": None,
        "vendor_id": 1,
        "uploaded_by": "admin",
        "uploaded_at": "2025-03-13T15:30:00Z",
        "file_size": 512000,
        "mime_type": "application/pdf"
    }
]

@router.post("/upload")
async def upload_document(
    request: Request,
    session: dict = Depends(require_auth),
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    vendor_id: Optional[int] = Form(None),
    document_type: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Upload a new document."""
    try:
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._-")
        unique_filename = f"{timestamp}_{safe_filename}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Determine file size
        file_size = os.path.getsize(file_path)
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Create document record in database
            document_data = {
                "filename": file.filename,
                "file_path": f"/static/uploads/{unique_filename}",
                "document_type": document_type,
                "description": description,
                "project_id": project_id,
                "vendor_id": vendor_id,
                "uploaded_by": session.get("username", "unknown"),
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_size": file_size,
                "mime_type": file.content_type
            }
            
            # Insert into database
            response = supabase_client.table("documents").insert(document_data).execute()
            
            if hasattr(response, 'data') and len(response.data) > 0:
                document_id = response.data[0].get("id")
            else:
                # If insert failed but file was saved, use a placeholder ID
                document_id = None
        else:
            # When Supabase is unavailable, just save the file and return success
            document_id = len(MOCK_DOCUMENTS) + 1  # Mock ID
            
        # Determine return URL based on context
        if project_id:
            return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
        elif vendor_id:
            return RedirectResponse(url=f"/vendors/{vendor_id}", status_code=303)
        else:
            return RedirectResponse(url="/", status_code=303)
            
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error uploading document. Please try again."
            }
        )

@router.get("/{document_id}")
async def view_document(
    request: Request,
    document_id: int,
    session: dict = Depends(require_auth),
    download: bool = False
):
    """View or download a document."""
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Get document from database
            response = supabase_client.table("documents").select("*").eq("id", document_id).execute()
            
            if hasattr(response, 'data') and len(response.data) > 0:
                document = response.data[0]
            else:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": "Document not found"
                    }
                )
        else:
            # Use mock data
            document = next((d for d in MOCK_DOCUMENTS if d["id"] == document_id), None)
            
            if not document:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": "Document not found"
                    }
                )
        
        # Extract file path from document record
        file_path = document.get("file_path")
        if file_path.startswith("/static/"):
            file_path = file_path[8:]  # Remove /static/ prefix
            
        absolute_path = Path("static") / file_path
        
        if not absolute_path.exists():
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": "Document file not found"
                }
            )
            
        filename = document.get("filename", "document")
        
        # Determine content disposition based on download parameter
        if download:
            return FileResponse(
                path=absolute_path,
                filename=filename,
                media_type=document.get("mime_type", "application/octet-stream")
            )
        else:
            # For viewing, use appropriate header based on file type
            mime_type = document.get("mime_type", "")
            
            if mime_type.startswith("image/"):
                # Images can be viewed directly
                return FileResponse(
                    path=absolute_path,
                    media_type=mime_type
                )
            elif mime_type == "application/pdf":
                # PDFs can be viewed in browser
                return FileResponse(
                    path=absolute_path,
                    media_type=mime_type
                )
            else:
                # For other file types, force download
                return FileResponse(
                    path=absolute_path,
                    filename=filename,
                    media_type=mime_type
                )
    except Exception as e:
        logging.error(f"Error retrieving document {document_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error retrieving document. Please try again."
            }
        )

@router.post("/{document_id}/delete")
async def delete_document(
    request: Request,
    document_id: int,
    session: dict = Depends(require_auth)
):
    """Delete a document."""
    try:
        supabase = get_supabase_client()
        
        # Get document details before deletion
        document = None
        if supabase:
            response = supabase.table("documents").select("*").eq("id", document_id).single().execute()
            if hasattr(response, 'data') and response.data:
                document = response.data
        else:
            document = next((d for d in MOCK_DOCUMENTS if d["id"] == document_id), None)
            
        if not document:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": "Document not found"
                }
            )
            
        # Delete file
        file_path = document.get("file_path", "")
        if file_path:
            if file_path.startswith("/static/"):
                file_path = file_path[8:]  # Remove /static/ prefix
                
            absolute_path = Path("static") / file_path
            if absolute_path.exists():
                absolute_path.unlink()
        
        # Delete database record
        if supabase:
            supabase.table("documents").delete().eq("id", document_id).execute()
            
            # Record activity
            activity_data = {
                "user_id": session.get("user_id"),
                "activity_type": "document_deleted",
                "description": f"Deleted document: {document.get('filename', 'unknown')}",
                "created_at": datetime.utcnow().isoformat()
            }
            
            if document.get("project_id"):
                activity_data["project_id"] = document.get("project_id")
            elif document.get("vendor_id"):
                activity_data["vendor_id"] = document.get("vendor_id")
                
            supabase.table("activities").insert(activity_data).execute()
        
        # Redirect based on context
        if document.get("project_id"):
            return RedirectResponse(url=f"/projects/{document.get('project_id')}", status_code=303)
        elif document.get("vendor_id"):
            return RedirectResponse(url=f"/vendors/{document.get('vendor_id')}", status_code=303)
        else:
            return RedirectResponse(url="/documents", status_code=303)
            
    except Exception as e:
        logging.error(f"Error deleting document {document_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error deleting document"
            }
        ) 