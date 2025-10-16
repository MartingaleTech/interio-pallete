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
