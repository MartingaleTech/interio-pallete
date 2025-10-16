from datetime import datetime
from typing import List
import uuid
from fastapi import HTTPException
from src.models import (
    Invoice, InvoiceCreate, OrgInvoice, OrgInvoiceCreate,
    User, UserRole, PaymentStatus
)
from src.database import (
    get_invoices_db, get_org_invoices_db, get_organizations_db,
    get_projects_db, get_clients_db
)


def create_org_invoice(org_id: str, invoice: OrgInvoiceCreate) -> OrgInvoice:
    """Create an invoice for an organization."""
    organizations_db = get_organizations_db()
    org_invoices_db = get_org_invoices_db()
    
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    invoice_id = str(uuid.uuid4())
    invoice_number = f"ORG-{len(org_invoices_db) + 1:05d}"
    
    new_invoice = OrgInvoice(
        id=invoice_id,
        org_id=org_id,
        invoice_number=invoice_number,
        subscription_plan=invoice.subscription_plan,
        amount=invoice.amount,
        payment_status=PaymentStatus.PENDING,
        billing_period_start=invoice.billing_period_start,
        billing_period_end=invoice.billing_period_end,
        due_date=invoice.due_date,
        created_at=datetime.now().isoformat()
    )
    org_invoices_db[invoice_id] = new_invoice
    
    return new_invoice


def get_org_invoices(org_id: str) -> List[OrgInvoice]:
    """Get all invoices for an organization."""
    organizations_db = get_organizations_db()
    org_invoices_db = get_org_invoices_db()
    
    if org_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    invoices = [inv for inv in org_invoices_db.values() if inv.org_id == org_id]
    return invoices


def create_project_invoice(user: User, project_id: str, invoice: InvoiceCreate) -> Invoice:
    """Create an invoice for a project."""
    projects_db = get_projects_db()
    invoices_db = get_invoices_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    invoice_id = str(uuid.uuid4())
    invoice_number = f"INV-{len(invoices_db) + 1:05d}"
    total = invoice.amount + invoice.tax
    
    new_invoice = Invoice(
        id=invoice_id,
        project_id=project_id,
        org_id=project.org_id,
        invoice_number=invoice_number,
        amount=invoice.amount,
        tax=invoice.tax,
        total=total,
        payment_status=PaymentStatus.PENDING,
        due_date=invoice.due_date,
        created_at=datetime.now().isoformat()
    )
    invoices_db[invoice_id] = new_invoice
    
    return new_invoice


def get_project_invoices(user: User, project_id: str) -> List[Invoice]:
    """Get all invoices for a project."""
    projects_db = get_projects_db()
    clients_db = get_clients_db()
    invoices_db = get_invoices_db()
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if user.role == UserRole.CLIENT:
        client = None
        for c in clients_db.values():
            if c.email == user.email and c.org_id == project.org_id:
                client = c
                break
        if not client or project.client_id != client.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif user.org_id != project.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    invoices = [inv for inv in invoices_db.values() if inv.project_id == project_id]
    return invoices
