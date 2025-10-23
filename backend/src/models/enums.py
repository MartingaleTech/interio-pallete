from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    ORG_OWNER = "org_owner"
    ORG_MEMBER = "org_member"
    CLIENT = "client"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketType(str, Enum):
    PROJECT_ISSUE = "project_issue"
    DESIGN_CHANGE = "design_change"
    CORRECTION = "correction"
    MISSING_ITEM = "missing_item"
    INTERIOR_WORK = "interior_work"
    APP_ISSUE = "app_issue"
    INVOICE_ISSUE = "invoice_issue"
    ACCESS_ISSUE = "access_issue"
    PLAN_ISSUE = "plan_issue"
    OTHER = "other"
