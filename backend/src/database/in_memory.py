from typing import Dict, List, Any
from src.models import (
    User, Organization, Project, Client, TeamMember,
    CalendarEvent, ProjectDesign, Invoice, OrgInvoice
)

users_db: Dict[str, User] = {}
passwords_db: Dict[str, str] = {}
tokens_db: Dict[str, str] = {}
organizations_db: Dict[str, Organization] = {}
projects_db: Dict[str, Project] = {}
clients_db: Dict[str, Client] = {}
team_members_db: Dict[str, List[TeamMember]] = {}
calendar_events_db: Dict[str, List[CalendarEvent]] = {}
project_designs_db: Dict[str, List[ProjectDesign]] = {}
invoices_db: Dict[str, Invoice] = {}
org_invoices_db: Dict[str, OrgInvoice] = {}
otp_db: Dict[str, Dict[str, Any]] = {}


def get_users_db() -> Dict[str, User]:
    return users_db


def get_passwords_db() -> Dict[str, str]:
    return passwords_db


def get_tokens_db() -> Dict[str, str]:
    return tokens_db


def get_organizations_db() -> Dict[str, Organization]:
    return organizations_db


def get_projects_db() -> Dict[str, Project]:
    return projects_db


def get_clients_db() -> Dict[str, Client]:
    return clients_db


def get_team_members_db() -> Dict[str, List[TeamMember]]:
    return team_members_db


def get_calendar_events_db() -> Dict[str, List[CalendarEvent]]:
    return calendar_events_db


def get_project_designs_db() -> Dict[str, List[ProjectDesign]]:
    return project_designs_db


def get_invoices_db() -> Dict[str, Invoice]:
    return invoices_db


def get_org_invoices_db() -> Dict[str, OrgInvoice]:
    return org_invoices_db


def get_otp_db() -> Dict[str, Dict[str, Any]]:
    return otp_db
