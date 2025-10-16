from pydantic import BaseModel
from typing import Optional
from .enums import PaymentStatus


class Invoice(BaseModel):
    id: str
    project_id: str
    org_id: str
    invoice_number: str
    amount: float
    tax: float
    total: float
    payment_status: PaymentStatus
    due_date: str
    paid_date: Optional[str] = None
    created_at: str


class InvoiceCreate(BaseModel):
    project_id: str
    amount: float
    tax: float
    due_date: str


class OrgInvoice(BaseModel):
    id: str
    org_id: str
    invoice_number: str
    subscription_plan: str
    amount: float
    payment_status: PaymentStatus
    billing_period_start: str
    billing_period_end: str
    due_date: str
    paid_date: Optional[str] = None
    created_at: str


class OrgInvoiceCreate(BaseModel):
    org_id: str
    subscription_plan: str
    amount: float
    billing_period_start: str
    billing_period_end: str
    due_date: str
