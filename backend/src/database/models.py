from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.database import Base
from src.models.enums import UserRole, SubscriptionStatus, ProjectStatus, PaymentStatus, TicketStatus, TicketPriority, TicketType
import enum


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    phone = Column(String, nullable=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="members", foreign_keys=[org_id])


class Token(Base):
    __tablename__ = "tokens"
    
    token = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")


class OTP(Base):
    __tablename__ = "otps"
    
    phone = Column(String, primary_key=True)
    otp = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    user = relationship("User")


class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_status = Column(SQLEnum(SubscriptionStatus), nullable=False)
    subscription_plan = Column(String, nullable=False)
    subscription_start = Column(DateTime, nullable=False)
    subscription_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("User", back_populates="organization", foreign_keys=[User.org_id])
    projects = relationship("Project", back_populates="organization")
    clients = relationship("Client", back_populates="organization")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(SQLEnum(ProjectStatus), nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    client_name = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="projects")
    client = relationship("Client", back_populates="projects")
    team_members = relationship("TeamMember", back_populates="project", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="project", cascade="all, delete-orphan")
    designs = relationship("ProjectDesign", back_populates="project", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="project", cascade="all, delete-orphan")
    notifications = relationship("ProjectNotification", back_populates="project", cascade="all, delete-orphan")
    daily_updates = relationship("ProjectDailyUpdate", back_populates="project", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="clients")
    projects = relationship("Project", back_populates="client")


class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    
    project = relationship("Project", back_populates="team_members")
    user = relationship("User")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    attendees = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="calendar_events")


class ProjectDesign(Base):
    __tablename__ = "project_designs"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="designs")


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    invoice_number = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), nullable=False)
    due_date = Column(String, nullable=False)
    paid_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="invoices")
    organization = relationship("Organization")


class OrgInvoice(Base):
    __tablename__ = "org_invoices"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    invoice_number = Column(String, unique=True, nullable=False)
    subscription_plan = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), nullable=False)
    billing_period_start = Column(String, nullable=False)
    billing_period_end = Column(String, nullable=False)
    due_date = Column(String, nullable=False)
    paid_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization")


class RecentlyViewedOrg(Base):
    __tablename__ = "recently_viewed_orgs"
    
    id = Column(String, primary_key=True)
    admin_id = Column(String, ForeignKey("users.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    viewed_at = Column(DateTime, default=datetime.utcnow)
    
    admin = relationship("User")
    organization = relationship("Organization")


class ProjectTicket(Base):
    __tablename__ = "project_tickets"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    ticket_type = Column(SQLEnum(TicketType), nullable=False)
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    project = relationship("Project")
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")


class OrgTicket(Base):
    __tablename__ = "org_tickets"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    ticket_type = Column(SQLEnum(TicketType), nullable=False)
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    comments = relationship("TicketComment", back_populates="org_ticket", cascade="all, delete-orphan")
    attachments = relationship("TicketAttachment", back_populates="org_ticket", cascade="all, delete-orphan")


class TicketComment(Base):
    __tablename__ = "ticket_comments"
    
    id = Column(String, primary_key=True)
    project_ticket_id = Column(String, ForeignKey("project_tickets.id"), nullable=True)
    org_ticket_id = Column(String, ForeignKey("org_tickets.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ticket = relationship("ProjectTicket", back_populates="comments")
    org_ticket = relationship("OrgTicket", back_populates="comments")
    user = relationship("User")


class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"
    
    id = Column(String, primary_key=True)
    project_ticket_id = Column(String, ForeignKey("project_tickets.id"), nullable=True)
    org_ticket_id = Column(String, ForeignKey("org_tickets.id"), nullable=True)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticket = relationship("ProjectTicket", back_populates="attachments")
    org_ticket = relationship("OrgTicket", back_populates="attachments")
    uploader = relationship("User")


class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization")
    creator = relationship("User")


class AdminNotification(Base):
    __tablename__ = "admin_notifications"
    
    id = Column(String, primary_key=True)
    admin_id = Column(String, ForeignKey("users.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    notification_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    admin = relationship("User")
    organization = relationship("Organization")


class ProjectNotification(Base):
    __tablename__ = "project_notifications"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    notification_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="notifications")
    organization = relationship("Organization")
    user = relationship("User")


class ProjectDailyUpdate(Base):
    __tablename__ = "project_daily_updates"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_name = Column(String, nullable=False)
    update_text = Column(Text, nullable=False)
    attachments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="daily_updates")
    organization = relationship("Organization")
    user = relationship("User")
