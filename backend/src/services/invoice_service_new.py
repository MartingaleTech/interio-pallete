from datetime import datetime
from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import (
    InvoiceCreate, User, UserRole, PaymentStatus, OrgInvoiceCreate
)
from src.repositories import InvoiceRepository, OrgInvoiceRepository, ProjectRepository, OrganizationRepository
from src.utils.mappers import db_invoice_to_pydantic, db_org_invoice_to_pydantic


def create_project_invoice(db: Session, user: User, project_id: str, invoice: InvoiceCreate):
    """Create an invoice for a project."""
    invoice_repo = InvoiceRepository(db)
    project_repo = ProjectRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if db_project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    invoice_id = str(uuid.uuid4())
    invoice_number = f"INV-{datetime.now().year}-{datetime.now().month:02d}-{uuid.uuid4().hex[:6].upper()}"
    
    invoice_data = {
        "id": invoice_id,
        "project_id": project_id,
        "org_id": user.org_id,
        "invoice_number": invoice_number,
        "amount": invoice.amount,
        "tax": invoice.tax,
        "total": invoice.amount + invoice.tax,
        "payment_status": PaymentStatus.PENDING,
        "due_date": invoice.due_date,
        "created_at": datetime.utcnow()
    }
    db_invoice = invoice_repo.create(invoice_data)
    
    return db_invoice_to_pydantic(db_invoice)


def get_project_invoices(db: Session, user: User, project_id: str) -> List:
    """Get all invoices for a project."""
    invoice_repo = InvoiceRepository(db)
    project_repo = ProjectRepository(db)
    
    db_project = project_repo.get_by_id(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user.role == UserRole.CLIENT:
        if db_project.client_id != user.email:
            raise HTTPException(status_code=403, detail="Access denied")
    elif db_project.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db_invoices = invoice_repo.get_by_project_id(project_id)
    return [db_invoice_to_pydantic(i) for i in db_invoices]


def create_org_invoice(db: Session, org_id: str, invoice: OrgInvoiceCreate):
    """Create an invoice for an organization (admin only)."""
    org_invoice_repo = OrgInvoiceRepository(db)
    org_repo = OrganizationRepository(db)
    
    db_org = org_repo.get_by_id(org_id)
    if not db_org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    invoice_id = str(uuid.uuid4())
    invoice_number = f"ORG-INV-{datetime.now().year}-{datetime.now().month:02d}-{uuid.uuid4().hex[:6].upper()}"
    
    invoice_data = {
        "id": invoice_id,
        "org_id": org_id,
        "invoice_number": invoice_number,
        "subscription_plan": invoice.subscription_plan,
        "amount": invoice.amount,
        "payment_status": PaymentStatus.PENDING,
        "billing_period_start": invoice.billing_period_start,
        "billing_period_end": invoice.billing_period_end,
        "due_date": invoice.due_date,
        "created_at": datetime.utcnow()
    }
    db_invoice = org_invoice_repo.create(invoice_data)
    
    return db_org_invoice_to_pydantic(db_invoice)


def get_org_invoices(db: Session, org_id: str) -> List:
    """Get all invoices for an organization (admin only)."""
    org_invoice_repo = OrgInvoiceRepository(db)
    org_repo = OrganizationRepository(db)
    
    if not org_repo.get_by_id(org_id):
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db_invoices = org_invoice_repo.get_by_org_id(org_id)
    return [db_org_invoice_to_pydantic(i) for i in db_invoices]
