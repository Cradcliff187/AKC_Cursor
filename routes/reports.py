from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
from datetime import datetime, timedelta
import json

from dependencies import get_session, get_supabase_client, check_auth, templates
from mock_data import (
    MOCK_TIME_LOGS,
    MOCK_EXPENSES,
    MOCK_PROJECTS,
    MOCK_VENDORS,
    MOCK_USERS,
    MOCK_ACTIVITY
)

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/", response_class=HTMLResponse)
async def show_reports(request: Request, session: dict = Depends(get_session)):
    """Show main reports dashboard"""
    if not check_auth(session):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please log in to access reports"})
    
    try:
        supabase = get_supabase_client()
        
        if supabase:
            # Get real data from Supabase
            projects = supabase.table("projects").select("*").execute().data
            expenses = supabase.table("expenses").select("*").execute().data
            time_logs = supabase.table("time_logs").select("*").execute().data
            vendors = supabase.table("vendors").select("*").execute().data
        else:
            # Use mock data
            projects = MOCK_PROJECTS
            expenses = MOCK_EXPENSES
            time_logs = MOCK_TIME_LOGS
            vendors = MOCK_VENDORS
            
        # Calculate report statistics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p["status"] == "In Progress"])
        total_expenses = sum(e["amount"] for e in expenses)
        total_hours = sum(t["hours"] for t in time_logs)
        total_vendors = len(vendors)
        active_vendors = len([v for v in vendors if v["status"] == "Active"])
        
        # Calculate monthly trends
        now = datetime.now()
        months = []
        expense_trend = []
        hours_trend = []
        
        for i in range(6):
            month = now - timedelta(days=30*i)
            months.insert(0, month.strftime("%b"))
            
            # Calculate monthly totals
            month_expenses = sum(e["amount"] for e in expenses if datetime.fromisoformat(e["date"]).strftime("%Y-%m") == month.strftime("%Y-%m"))
            month_hours = sum(t["hours"] for t in time_logs if datetime.fromisoformat(t["date"]).strftime("%Y-%m") == month.strftime("%Y-%m"))
            
            expense_trend.insert(0, month_expenses)
            hours_trend.insert(0, month_hours)
        
        # Prepare report data
        report_data = {
            "summary": {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "total_expenses": total_expenses,
                "total_hours": total_hours,
                "total_vendors": total_vendors,
                "active_vendors": active_vendors
            },
            "trends": {
                "months": months,
                "expenses": expense_trend,
                "hours": hours_trend
            },
            "recent_activity": MOCK_ACTIVITY[:5]  # Show 5 most recent activities
        }
        
        return templates.TemplateResponse(
            "reports/dashboard.html",
            {
                "request": request,
                "session": session,
                "report_data": report_data
            }
        )
    except Exception as e:
        print(f"Error in reports dashboard: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading reports dashboard"
            }
        )

@router.get("/time", response_class=HTMLResponse)
async def time_reports(
    request: Request,
    session: dict = Depends(get_session),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """Show time tracking reports"""
    if not check_auth(session):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please log in to access time reports"})
    
    try:
        supabase = get_supabase_client()
        
        if supabase:
            # Get real data from Supabase with filters
            query = supabase.table("time_logs").select("*, projects(name), users(name)")
            
            if start_date:
                query = query.gte("date", start_date)
            if end_date:
                query = query.lte("date", end_date)
            if project_id:
                query = query.eq("project_id", project_id)
            if user_id:
                query = query.eq("user_id", user_id)
                
            time_logs = query.execute().data
            projects = supabase.table("projects").select("*").execute().data
            users = supabase.table("users").select("*").execute().data
        else:
            # Use mock data
            time_logs = MOCK_TIME_LOGS
            projects = MOCK_PROJECTS
            users = MOCK_USERS
            
            # Apply filters to mock data
            if start_date:
                time_logs = [t for t in time_logs if t["date"] >= start_date]
            if end_date:
                time_logs = [t for t in time_logs if t["date"] <= end_date]
            if project_id:
                time_logs = [t for t in time_logs if t["project_id"] == project_id]
            if user_id:
                time_logs = [t for t in time_logs if t["user_id"] == user_id]
        
        # Calculate time report statistics
        total_hours = sum(t["hours"] for t in time_logs)
        avg_hours_per_day = total_hours / len(set(t["date"] for t in time_logs)) if time_logs else 0
        
        # Group hours by project
        project_hours = {}
        for log in time_logs:
            project_id = log["project_id"]
            project_name = next((p["name"] for p in projects if p["id"] == project_id), "Unknown")
            project_hours[project_name] = project_hours.get(project_name, 0) + log["hours"]
        
        # Group hours by user
        user_hours = {}
        for log in time_logs:
            user_id = log["user_id"]
            user_name = next((u["name"] for u in users if u["id"] == user_id), "Unknown")
            user_hours[user_name] = user_hours.get(user_name, 0) + log["hours"]
        
        return templates.TemplateResponse(
            "reports/time.html",
            {
                "request": request,
                "session": session,
                "time_logs": time_logs,
                "projects": projects,
                "users": users,
                "total_hours": total_hours,
                "avg_hours_per_day": avg_hours_per_day,
                "project_hours": project_hours,
                "user_hours": user_hours,
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "project_id": project_id,
                    "user_id": user_id
                }
            }
        )
    except Exception as e:
        print(f"Error in time reports: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading time reports"
            }
        )

@router.get("/expenses", response_class=HTMLResponse)
async def expense_reports(
    request: Request,
    session: dict = Depends(get_session),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    category: Optional[str] = None
):
    """Show expense reports"""
    if not check_auth(session):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please log in to access expense reports"})
    
    try:
        supabase = get_supabase_client()
        
        if supabase:
            # Get real data from Supabase with filters
            query = supabase.table("expenses").select("*, projects(name), vendors(name)")
            
            if start_date:
                query = query.gte("date", start_date)
            if end_date:
                query = query.lte("date", end_date)
            if project_id:
                query = query.eq("project_id", project_id)
            if vendor_id:
                query = query.eq("vendor_id", vendor_id)
            if category:
                query = query.eq("category", category)
                
            expenses = query.execute().data
            projects = supabase.table("projects").select("*").execute().data
            vendors = supabase.table("vendors").select("*").execute().data
        else:
            # Use mock data
            expenses = MOCK_EXPENSES
            projects = MOCK_PROJECTS
            vendors = MOCK_VENDORS
            
            # Apply filters to mock data
            if start_date:
                expenses = [e for e in expenses if e["date"] >= start_date]
            if end_date:
                expenses = [e for e in expenses if e["date"] <= end_date]
            if project_id:
                expenses = [e for e in expenses if e["project_id"] == project_id]
            if vendor_id:
                expenses = [e for e in expenses if e["vendor_id"] == vendor_id]
            if category:
                expenses = [e for e in expenses if e["category"] == category]
        
        # Calculate expense report statistics
        total_expenses = sum(e["amount"] for e in expenses)
        avg_expense = total_expenses / len(expenses) if expenses else 0
        
        # Group expenses by project
        project_expenses = {}
        for expense in expenses:
            project_id = expense["project_id"]
            project_name = next((p["name"] for p in projects if p["id"] == project_id), "Unknown")
            project_expenses[project_name] = project_expenses.get(project_name, 0) + expense["amount"]
        
        # Group expenses by vendor
        vendor_expenses = {}
        for expense in expenses:
            vendor_id = expense["vendor_id"]
            vendor_name = next((v["name"] for v in vendors if v["id"] == vendor_id), "Unknown")
            vendor_expenses[vendor_name] = vendor_expenses.get(vendor_name, 0) + expense["amount"]
        
        # Group expenses by category
        category_expenses = {}
        for expense in expenses:
            category = expense["category"]
            category_expenses[category] = category_expenses.get(category, 0) + expense["amount"]
        
        return templates.TemplateResponse(
            "reports/expenses.html",
            {
                "request": request,
                "session": session,
                "expenses": expenses,
                "projects": projects,
                "vendors": vendors,
                "total_expenses": total_expenses,
                "avg_expense": avg_expense,
                "project_expenses": project_expenses,
                "vendor_expenses": vendor_expenses,
                "category_expenses": category_expenses,
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "project_id": project_id,
                    "vendor_id": vendor_id,
                    "category": category
                }
            }
        )
    except Exception as e:
        print(f"Error in expense reports: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading expense reports"
            }
        )

@router.get("/projects", response_class=HTMLResponse)
async def project_reports(
    request: Request,
    session: dict = Depends(get_session),
    status: Optional[str] = None,
    client_id: Optional[int] = None
):
    """Show project reports and analytics"""
    if not check_auth(session):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Please log in to access project reports"})
    
    try:
        supabase = get_supabase_client()
        
        if supabase:
            # Get real data from Supabase with filters
            query = supabase.table("projects").select("*")
            
            if status:
                query = query.eq("status", status)
            if client_id:
                query = query.eq("client_id", client_id)
                
            projects = query.execute().data
            expenses = supabase.table("expenses").select("*").execute().data
            time_logs = supabase.table("time_logs").select("*").execute().data
        else:
            # Use mock data
            projects = MOCK_PROJECTS
            expenses = MOCK_EXPENSES
            time_logs = MOCK_TIME_LOGS
            
            # Apply filters to mock data
            if status:
                projects = [p for p in projects if p["status"] == status]
            if client_id:
                projects = [p for p in projects if p["client_id"] == client_id]
        
        # Calculate project statistics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p["status"] == "In Progress"])
        completed_projects = len([p for p in projects if p["status"] == "Completed"])
        
        # Calculate project costs and hours
        project_metrics = {}
        for project in projects:
            project_id = project["id"]
            project_expenses = sum(e["amount"] for e in expenses if e["project_id"] == project_id)
            project_hours = sum(t["hours"] for t in time_logs if t["project_id"] == project_id)
            
            project_metrics[project["name"]] = {
                "expenses": project_expenses,
                "hours": project_hours,
                "status": project["status"],
                "start_date": project["start_date"],
                "end_date": project.get("end_date"),
                "budget": project.get("budget", 0)
            }
        
        return templates.TemplateResponse(
            "reports/projects.html",
            {
                "request": request,
                "session": session,
                "projects": projects,
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "project_metrics": project_metrics,
                "filters": {
                    "status": status,
                    "client_id": client_id
                }
            }
        )
    except Exception as e:
        print(f"Error in project reports: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading project reports"
            }
        )

@router.get("/export")
async def export_report(
    request: Request,
    session: dict = Depends(get_session),
    report_type: str = Query(..., description="Type of report to export (time, expenses, projects)"),
    format: str = Query("csv", description="Export format (csv or json)")
):
    """Export report data"""
    if not check_auth(session):
        return JSONResponse(
            status_code=401,
            content={"error": "Please log in to export reports"}
        )
    
    try:
        supabase = get_supabase_client()
        
        if supabase:
            if report_type == "time":
                data = supabase.table("time_logs").select("*").execute().data
            elif report_type == "expenses":
                data = supabase.table("expenses").select("*").execute().data
            elif report_type == "projects":
                data = supabase.table("projects").select("*").execute().data
            else:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Invalid report type: {report_type}"}
                )
        else:
            # Use mock data
            if report_type == "time":
                data = MOCK_TIME_LOGS
            elif report_type == "expenses":
                data = MOCK_EXPENSES
            elif report_type == "projects":
                data = MOCK_PROJECTS
            else:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Invalid report type: {report_type}"}
                )
        
        if format == "json":
            return JSONResponse(content=data)
        elif format == "csv":
            # Convert data to CSV format
            if not data:
                return JSONResponse(
                    status_code=404,
                    content={"error": "No data found"}
                )
            
            headers = list(data[0].keys())
            csv_data = ",".join(headers) + "\n"
            
            for row in data:
                csv_data += ",".join(str(row.get(h, "")) for h in headers) + "\n"
            
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="{report_type}_report.csv"'
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid format: {format}"}
            )
            
    except Exception as e:
        print(f"Error exporting report: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error exporting report"}
        ) 