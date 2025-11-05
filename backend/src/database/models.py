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
    expires_at = Column(DateTime, nullable=False)
    
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
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    uploaded_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    uploaded_by = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, nullable=False, default=1)
    parent_id = Column(String, ForeignKey("project_designs.id"), nullable=True)
    is_latest_version = Column(Boolean, nullable=False, default=True)
    thumbnail_url = Column(String, nullable=True)
    is_public = Column(Boolean, nullable=False, default=False)
    download_count = Column(Integer, nullable=False, default=0)
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    project = relationship("Project", back_populates="designs")
    uploader = relationship("User", foreign_keys=[uploaded_by_id])
    parent = relationship("ProjectDesign", remote_side=[id], foreign_keys=[parent_id])
    comments = relationship("FileComment", back_populates="file", cascade="all, delete-orphan")
    permissions = relationship("FilePermission", back_populates="file", cascade="all, delete-orphan")
    audit_logs = relationship("FileAuditLog", back_populates="file", cascade="all, delete-orphan")


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


class FileComment(Base):
    __tablename__ = "file_comments"
    
    id = Column(String, primary_key=True)
    file_id = Column(String, ForeignKey("project_designs.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_name = Column(String, nullable=False)
    comment = Column(Text, nullable=False)
    parent_comment_id = Column(String, ForeignKey("file_comments.id"), nullable=True)
    mentions = Column(Text, nullable=True)
    is_resolved = Column(Boolean, nullable=False, default=False)
    resolved_by = Column(String, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    file = relationship("ProjectDesign", back_populates="comments")
    project = relationship("Project")
    organization = relationship("Organization")
    user = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
    parent_comment = relationship("FileComment", remote_side=[id], foreign_keys=[parent_comment_id])


class FilePermission(Base):
    __tablename__ = "file_permissions"
    
    id = Column(String, primary_key=True)
    file_id = Column(String, ForeignKey("project_designs.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    role = Column(String, nullable=True)
    can_view = Column(Boolean, nullable=False, default=True)
    can_download = Column(Boolean, nullable=False, default=True)
    can_comment = Column(Boolean, nullable=False, default=True)
    can_delete = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    file = relationship("ProjectDesign", back_populates="permissions")
    user = relationship("User")


class FileAuditLog(Base):
    __tablename__ = "file_audit_logs"
    
    id = Column(String, primary_key=True)
    file_id = Column(String, ForeignKey("project_designs.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    action_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    file = relationship("ProjectDesign", back_populates="audit_logs")
    user = relationship("User")


class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project")
    organization = relationship("Organization")
    creator = relationship("User", foreign_keys=[created_by])
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")
    participants = relationship("ChatRoomParticipant", back_populates="room", cascade="all, delete-orphan")


class ChatRoomParticipant(Base):
    __tablename__ = "chat_room_participants"
    
    id = Column(String, primary_key=True)
    room_id = Column(String, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_read_at = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)
    
    room = relationship("ChatRoom", back_populates="participants")
    user = relationship("User")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True)
    room_id = Column(String, ForeignKey("chat_rooms.id"), nullable=True)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    sender_name = Column(String, nullable=False)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    message_type = Column(String, nullable=False, default="text")
    attachment_url = Column(String, nullable=True)
    attachment_name = Column(String, nullable=True)
    attachment_type = Column(String, nullable=True)
    attachment_size = Column(Integer, nullable=True)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_for_everyone = Column(Boolean, default=False)
    parent_message_id = Column(String, ForeignKey("chat_messages.id"), nullable=True)
    mentions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    parent_message = relationship("ChatMessage", remote_side=[id], foreign_keys=[parent_message_id])
    read_receipts = relationship("MessageReadReceipt", back_populates="message", cascade="all, delete-orphan")


class MessageReadReceipt(Base):
    __tablename__ = "message_read_receipts"
    
    id = Column(String, primary_key=True)
    message_id = Column(String, ForeignKey("chat_messages.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    
    message = relationship("ChatMessage", back_populates="read_receipts")
    user = relationship("User")


class TypingStatus(Base):
    __tablename__ = "typing_status"
    
    id = Column(String, primary_key=True)
    room_id = Column(String, ForeignKey("chat_rooms.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=True)
    is_typing = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    room = relationship("ChatRoom")
    user = relationship("User", foreign_keys=[user_id])
    recipient = relationship("User", foreign_keys=[recipient_id])


class ChatNotificationSettings(Base):
    __tablename__ = "chat_notification_settings"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    show_read_receipts = Column(Boolean, default=True)
    show_typing_indicators = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")
