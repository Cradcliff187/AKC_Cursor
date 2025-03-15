from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import traceback
import csv
import io

from dependencies import get_session, get_supabase_client, check_auth, templates
from routes.auth import require_auth
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
async def show_reports(request: Request, session: dict = Depends(require_auth)):
    """Show main reports dashboard"""
    try:
        supabase = get_supabase_client()
        
        # In real implementation, fetch summary stats from Supabase
        # For now, use mock data
        
        # Time tracking stats
        total_hours = sum(log.get("hours", 0) for log in MOCK_TIME_LOGS)
        billable_hours = sum(log.get("hours", 0) for log in MOCK_TIME_LOGS if log.get("billable", False))
        billable_percentage = round((billable_hours / total_hours * 100) if total_hours > 0 else 0, 1)
        
        # Expense stats
        total_expenses = sum(expense.get("amount", 0) for expense in MOCK_EXPENSES)
        expense_categories = {}
        for expense in MOCK_EXPENSES:
            category = expense.get("category", "Other")
            if category in expense_categories:
                expense_categories[category] += expense.get("amount", 0)
            else:
                expense_categories[category] = expense.get("amount", 0)
        
        # Project stats
        active_projects = len([p for p in MOCK_PROJECTS if p.get("status") == "in_progress"])
        completed_projects = len([p for p in MOCK_PROJECTS if p.get("status") == "completed"])
        
        # Prepare context
        context = {
            "request": request,
            "session": session,
            "time_stats": {
                "total_hours": total_hours,
                "billable_hours": billable_hours,
                "billable_percentage": billable_percentage
            },
            "expense_stats": {
                "total_expenses": total_expenses,
                "categories": expense_categories
            },
            "project_stats": {
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "total_projects": len(MOCK_PROJECTS)
            }
        }
        
        return templates.TemplateResponse("reports.html", context)
    except Exception as e:
        logging.error(f"Error loading reports dashboard: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading reports dashboard"
            }
        )

@router.get("/time", response_class=HTMLResponse)
async def time_reports(
    request: Request,
    session: dict = Depends(require_auth),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """Generate time reports with filtering options"""
    try:
        # Set default date range if not provided (last 30 days)
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Convert string dates to datetime objects for comparison
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Filter time logs based on criteria
        filtered_logs = MOCK_TIME_LOGS
        
        # Apply date filter
        filtered_logs = [
            log for log in filtered_logs 
            if start_dt <= datetime.strptime(log["date"], "%Y-%m-%d") <= end_dt
        ]
        
        # Apply project filter if specified
        if project_id:
            filtered_logs = [log for log in filtered_logs if log["project_id"] == project_id]
            
        # Apply user filter if specified
        if user_id:
            filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
        
        # Calculate summary statistics
        total_hours = sum(log["hours"] for log in filtered_logs)
        billable_hours = sum(log["hours"] for log in filtered_logs if log.get("billable", False))
        
        # Group by project
        project_hours = {}
        for log in filtered_logs:
            project_id = log["project_id"]
            project_name = next((p["name"] for p in MOCK_PROJECTS if p["id"] == project_id), "Unknown Project")
            
            if project_id not in project_hours:
                project_hours[project_id] = {
                    "id": project_id,
                    "name": project_name,
                    "hours": 0,
                    "billable_hours": 0
                }
            
            project_hours[project_id]["hours"] += log["hours"]
            if log.get("billable", False):
                project_hours[project_id]["billable_hours"] += log["hours"]
        
        # Group by user
        user_hours = {}
        for log in filtered_logs:
            user_id = log["user_id"]
            user_name = next((u["name"] for u in MOCK_USERS if u["id"] == user_id), "Unknown User")
            
            if user_id not in user_hours:
                user_hours[user_id] = {
                    "id": user_id,
                    "name": user_name,
                    "hours": 0,
                    "billable_hours": 0
                }
            
            user_hours[user_id]["hours"] += log["hours"]
            if log.get("billable", False):
                user_hours[user_id]["billable_hours"] += log["hours"]
        
        # Group by date for trend chart
        date_hours = {}
        for log in filtered_logs:
            date = log["date"]
            
            if date not in date_hours:
                date_hours[date] = {
                    "date": date,
                    "hours": 0,
                    "billable_hours": 0
                }
            
            date_hours[date]["hours"] += log["hours"]
            if log.get("billable", False):
                date_hours[date]["billable_hours"] += log["hours"]
        
        # Sort date data by date
        date_data = sorted(date_hours.values(), key=lambda x: x["date"])
        
        # Get available projects and users for filter dropdowns
        projects = MOCK_PROJECTS
        users = MOCK_USERS
        
        return templates.TemplateResponse(
            "reports/time.html",
            {
                "request": request,
                "session": session,
                "time_logs": filtered_logs,
                "projects": projects,
                "users": users,
                "selected_project_id": project_id,
                "selected_user_id": user_id,
                "start_date": start_date,
                "end_date": end_date,
                "total_hours": total_hours,
                "billable_hours": billable_hours,
                "billable_percentage": round((billable_hours / total_hours * 100) if total_hours > 0 else 0, 1),
                "project_hours": list(project_hours.values()),
                "user_hours": list(user_hours.values()),
                "date_data": date_data
            }
        )
    except Exception as e:
        logging.error(f"Error generating time reports: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error generating time reports"
            }
        )

@router.get("/expenses", response_class=HTMLResponse)
async def expense_reports(
    request: Request,
    session: dict = Depends(require_auth),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    category: Optional[str] = None
):
    """Generate expense reports with filtering options"""
    try:
        # Set default date range if not provided (last 30 days)
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Convert string dates to datetime objects for comparison
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Filter expenses based on criteria
        filtered_expenses = MOCK_EXPENSES
        
        # Apply date filter
        filtered_expenses = [
            expense for expense in filtered_expenses 
            if start_dt <= datetime.strptime(expense["date"], "%Y-%m-%d") <= end_dt
        ]
        
        # Apply project filter if specified
        if project_id:
            filtered_expenses = [expense for expense in filtered_expenses if expense["project_id"] == project_id]
            
        # Apply vendor filter if specified
        if vendor_id:
            filtered_expenses = [expense for expense in filtered_expenses if expense["vendor_id"] == vendor_id]
            
        # Apply category filter if specified
        if category:
            filtered_expenses = [expense for expense in filtered_expenses if expense["category"] == category]
        
        # Calculate summary statistics
        total_amount = sum(expense["amount"] for expense in filtered_expenses)
        
        # Group by project
        project_expenses = {}
        for expense in filtered_expenses:
            project_id = expense["project_id"]
            project_name = next((p["name"] for p in MOCK_PROJECTS if p["id"] == project_id), "Unknown Project")
            
            if project_id not in project_expenses:
                project_expenses[project_id] = {
                    "id": project_id,
                    "name": project_name,
                    "amount": 0
                }
            
            project_expenses[project_id]["amount"] += expense["amount"]
        
        # Group by vendor
        vendor_expenses = {}
        for expense in filtered_expenses:
            vendor_id = expense["vendor_id"]
            vendor_name = next((v["name"] for v in MOCK_VENDORS if v["id"] == vendor_id), "Unknown Vendor")
            
            if vendor_id not in vendor_expenses:
                vendor_expenses[vendor_id] = {
                    "id": vendor_id,
                    "name": vendor_name,
                    "amount": 0
                }
            
            vendor_expenses[vendor_id]["amount"] += expense["amount"]
        
        # Group by category
        category_expenses = {}
        for expense in filtered_expenses:
            cat = expense["category"]
            
            if cat not in category_expenses:
                category_expenses[cat] = {
                    "category": cat,
                    "amount": 0
                }
            
            category_expenses[cat]["amount"] += expense["amount"]
        
        # Group by date for trend chart
        date_expenses = {}
        for expense in filtered_expenses:
            date = expense["date"]
            
            if date not in date_expenses:
                date_expenses[date] = {
                    "date": date,
                    "amount": 0
                }
            
            date_expenses[date]["amount"] += expense["amount"]
        
        # Sort date data by date
        date_data = sorted(date_expenses.values(), key=lambda x: x["date"])
        
        # Get available projects, vendors, and categories for filter dropdowns
        projects = MOCK_PROJECTS
        vendors = MOCK_VENDORS
        categories = list(set(e["category"] for e in MOCK_EXPENSES))
        
        return templates.TemplateResponse(
            "reports/expenses.html",
            {
                "request": request,
                "session": session,
                "expenses": filtered_expenses,
                "projects": projects,
                "vendors": vendors,
                "categories": categories,
                "selected_project_id": project_id,
                "selected_vendor_id": vendor_id,
                "selected_category": category,
                "start_date": start_date,
                "end_date": end_date,
                "total_amount": total_amount,
                "project_expenses": list(project_expenses.values()),
                "vendor_expenses": list(vendor_expenses.values()),
                "category_expenses": list(category_expenses.values()),
                "date_data": date_data
            }
        )
    except Exception as e:
        logging.error(f"Error generating expense reports: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error generating expense reports"
            }
        )

@router.get("/projects", response_class=HTMLResponse)
async def project_reports(
    request: Request,
    session: dict = Depends(require_auth),
    status: Optional[str] = None,
    client_id: Optional[int] = None
):
    """Generate project profitability and status reports"""
    try:
        # Filter projects based on criteria
        filtered_projects = MOCK_PROJECTS
        
        # Apply status filter if specified
        if status:
            filtered_projects = [project for project in filtered_projects if project["status"] == status]
            
        # Apply client filter if specified
        if client_id:
            filtered_projects = [project for project in filtered_projects if project.get("client_id") == client_id]
        
        # Enhance projects with profitability data
        enhanced_projects = []
        for project in filtered_projects:
            project_id = project["id"]
            
            # Get time logs for this project
            project_time_logs = [log for log in MOCK_TIME_LOGS if log["project_id"] == project_id]
            total_hours = sum(log["hours"] for log in project_time_logs)
            billable_hours = sum(log["hours"] for log in project_time_logs if log.get("billable", False))
            
            # Calculate labor cost and revenue
            labor_cost = sum(log["hours"] * log.get("hourly_cost", 25) for log in project_time_logs)
            labor_revenue = sum(log["hours"] * log.get("hourly_rate", 50) for log in project_time_logs if log.get("billable", False))
            
            # Get expenses for this project
            project_expenses = [expense for expense in MOCK_EXPENSES if expense["project_id"] == project_id]
            total_expenses = sum(expense["amount"] for expense in project_expenses)
            
            # Calculate profitability
            total_cost = labor_cost + total_expenses
            total_revenue = labor_revenue + project.get("additional_revenue", 0)
            profit = total_revenue - total_cost
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Add enhanced data
            enhanced_project = {
                **project,
                "total_hours": total_hours,
                "billable_hours": billable_hours,
                "labor_cost": labor_cost,
                "labor_revenue": labor_revenue,
                "total_expenses": total_expenses,
                "total_cost": total_cost,
                "total_revenue": total_revenue,
                "profit": profit,
                "profit_margin": profit_margin
            }
            
            enhanced_projects.append(enhanced_project)
        
        # Sort projects by profit margin
        enhanced_projects.sort(key=lambda p: p["profit_margin"], reverse=True)
        
        # Calculate overall stats
        total_revenue = sum(p["total_revenue"] for p in enhanced_projects)
        total_cost = sum(p["total_cost"] for p in enhanced_projects)
        total_profit = sum(p["profit"] for p in enhanced_projects)
        average_margin = sum(p["profit_margin"] for p in enhanced_projects) / len(enhanced_projects) if enhanced_projects else 0
        
        # Get available statuses and clients for filter dropdowns
        statuses = list(set(p["status"] for p in MOCK_PROJECTS))
        clients = []  # Would get from database
        
        return templates.TemplateResponse(
            "reports/projects.html",
            {
                "request": request,
                "session": session,
                "projects": enhanced_projects,
                "statuses": statuses,
                "clients": clients,
                "selected_status": status,
                "selected_client_id": client_id,
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "total_profit": total_profit,
                "average_margin": average_margin,
                "project_count": len(enhanced_projects)
            }
        )
    except Exception as e:
        logging.error(f"Error generating project reports: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error generating project reports"
            }
        )

@router.get("/export")
async def export_report(
    request: Request,
    session: dict = Depends(require_auth),
    report_type: str = Query(..., description="Type of report to export (time, expenses, projects)"),
    format: str = Query("csv", description="Export format (csv or json)")
):
    """Export report data to CSV or JSON"""
    try:
        # Ensure user has permission to export reports
        
        data = []
        
        # Get report data based on type
        if report_type == "time":
            # Get time logs
            time_logs = MOCK_TIME_LOGS
            
            # Enhance with project and user names
            for log in time_logs:
                project_name = next((p["name"] for p in MOCK_PROJECTS if p["id"] == log["project_id"]), "Unknown")
                user_name = next((u["name"] for u in MOCK_USERS if u["id"] == log["user_id"]), "Unknown")
                
                data.append({
                    "date": log["date"],
                    "project": project_name,
                    "user": user_name,
                    "hours": log["hours"],
                    "billable": "Yes" if log.get("billable", False) else "No",
                    "description": log.get("description", "")
                })
                
        elif report_type == "expenses":
            # Get expenses
            expenses = MOCK_EXPENSES
            
            # Enhance with project and vendor names
            for expense in expenses:
                project_name = next((p["name"] for p in MOCK_PROJECTS if p["id"] == expense["project_id"]), "Unknown")
                vendor_name = next((v["name"] for v in MOCK_VENDORS if v["id"] == expense["vendor_id"]), "Unknown")
                
                data.append({
                    "date": expense["date"],
                    "project": project_name,
                    "vendor": vendor_name,
                    "category": expense["category"],
                    "amount": expense["amount"],
                    "description": expense.get("description", "")
                })
                
        elif report_type == "projects":
            # Get projects with profitability data (simplified from project_reports endpoint)
            for project in MOCK_PROJECTS:
                project_id = project["id"]
                
                # Get time logs for this project
                project_time_logs = [log for log in MOCK_TIME_LOGS if log["project_id"] == project_id]
                total_hours = sum(log["hours"] for log in project_time_logs)
                
                # Get expenses for this project
                project_expenses = [expense for expense in MOCK_EXPENSES if expense["project_id"] == project_id]
                total_expenses = sum(expense["amount"] for expense in project_expenses)
                
                data.append({
                    "name": project["name"],
                    "status": project["status"],
                    "start_date": project.get("start_date", ""),
                    "end_date": project.get("end_date", ""),
                    "total_hours": total_hours,
                    "total_expenses": total_expenses
                })
        else:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")
        
        # Export data in requested format
        if format == "json":
            return JSONResponse(content=data)
        elif format == "csv":
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            
            # Set content to CSV format
            content = output.getvalue()
            
            # Create a response with appropriate content type
            response = JSONResponse(content={"csv_content": content})
            response.headers["Content-Disposition"] = f"attachment; filename={report_type}_report.csv"
            return response
        else:
            raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error exporting report: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error exporting report data") 