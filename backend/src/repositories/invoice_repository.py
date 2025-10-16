from sqlalchemy.orm import Session
from typing import Optional, List
from src.database import models


class InvoiceRepository:
    """Repository for Invoice database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, invoice_data: dict) -> models.Invoice:
        """Create an invoice."""
        db_invoice = models.Invoice(**invoice_data)
        self.db.add(db_invoice)
        self.db.commit()
        self.db.refresh(db_invoice)
        return db_invoice
    
    def get_by_project_id(self, project_id: str) -> List[models.Invoice]:
        """Get all invoices for a project."""
        return self.db.query(models.Invoice).filter(models.Invoice.project_id == project_id).all()


class OrgInvoiceRepository:
    """Repository for OrgInvoice database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, invoice_data: dict) -> models.OrgInvoice:
        """Create an organization invoice."""
        db_invoice = models.OrgInvoice(**invoice_data)
        self.db.add(db_invoice)
        self.db.commit()
        self.db.refresh(db_invoice)
        return db_invoice
    
    def get_by_org_id(self, org_id: str) -> List[models.OrgInvoice]:
        """Get all invoices for an organization."""
        return self.db.query(models.OrgInvoice).filter(models.OrgInvoice.org_id == org_id).all()
