"""
Route modules for the AKC CRM application.

This package contains all the route handlers for the application,
organized into separate modules by feature area.
"""

# Import all routers explicitly for clarity
from routes.auth import router as auth_router
from routes.contacts import router as contacts_router
from routes.customers import router as customers_router
from routes.documents import router as documents_router
from routes.expenses import router as expenses_router
from routes.invoices import router as invoices_router
from routes.projects import router as projects_router
from routes.reports import router as reports_router
from routes.time_logs import router as time_logs_router
from routes.vendors import router as vendors_router

# Create module objects with router attributes to match app.py expectations
class AuthModule:
    router = auth_router

class ContactsModule:
    router = contacts_router

class CustomersModule:
    router = customers_router

class DocumentsModule:
    router = documents_router

class ExpensesModule:
    router = expenses_router

class InvoicesModule:
    router = invoices_router

class ProjectsModule:
    router = projects_router

class ReportsModule:
    router = reports_router

class TimeLogsModule:
    router = time_logs_router

class VendorsModule:
    router = vendors_router

# Provide shorthand access to keep app.py cleaner
auth = AuthModule()
contacts = ContactsModule()
customers = CustomersModule()
documents = DocumentsModule()
expenses = ExpensesModule()
invoices = InvoicesModule()
projects = ProjectsModule()
reports = ReportsModule()
time_logs = TimeLogsModule()
vendors = VendorsModule() 