# Support Ticket System Documentation

## Overview

The Support Ticket System is a comprehensive ticketing solution that operates at two levels:

1. **Project-Level Tickets**: For clients and project team members to track issues, changes, and corrections within specific projects
2. **Organization-Level Tickets**: For organization admins to raise issues with super admins regarding app functionality, invoices, plans, and access

## Architecture

### Database Models

#### ProjectTicket
- **Purpose**: Tickets raised within a project context
- **Fields**:
  - `id`: Unique identifier
  - `project_id`: Associated project
  - `org_id`: Organization owning the project
  - `created_by`: User who created the ticket
  - `assigned_to`: User assigned to resolve the ticket (optional)
  - `title`: Ticket title
  - `description`: Detailed description
  - `ticket_type`: Type of ticket (design_change, correction, missing_item, etc.)
  - `status`: Current status (open, in_progress, resolved, closed, reopened)
  - `priority`: Priority level (low, medium, high, urgent)
  - `created_at`, `updated_at`, `resolved_at`: Timestamps

#### OrgTicket
- **Purpose**: Tickets raised by org admins to super admins
- **Fields**: Similar to ProjectTicket but without project_id
- **Use Cases**: App issues, invoice problems, plan changes, access issues

#### TicketComment
- **Purpose**: Comments and notes on tickets
- **Fields**:
  - `id`: Unique identifier
  - `project_ticket_id` or `org_ticket_id`: Associated ticket
  - `user_id`: Comment author
  - `comment`: Comment text
  - `is_internal`: Whether comment is internal (not visible to clients)
  - `created_at`, `updated_at`: Timestamps

#### TicketAttachment
- **Purpose**: File attachments for tickets
- **Fields**:
  - `id`: Unique identifier
  - `project_ticket_id` or `org_ticket_id`: Associated ticket
  - `uploaded_by`: User who uploaded
  - `file_name`, `file_url`, `file_type`, `file_size`: File metadata
  - `created_at`: Timestamp

### Enums

#### TicketStatus
- `OPEN`: Newly created ticket
- `IN_PROGRESS`: Being worked on
- `RESOLVED`: Issue resolved, awaiting confirmation
- `CLOSED`: Ticket closed
- `REOPENED`: Reopened after being closed

#### TicketPriority
- `LOW`: Low priority
- `MEDIUM`: Medium priority (default)
- `HIGH`: High priority
- `URGENT`: Urgent, needs immediate attention

#### TicketType
- `PROJECT_ISSUE`: General project issue
- `DESIGN_CHANGE`: Design modification request
- `CORRECTION`: Correction needed
- `MISSING_ITEM`: Missing item in project
- `INTERIOR_WORK`: Interior work change
- `APP_ISSUE`: Application issue (org tickets)
- `INVOICE_ISSUE`: Invoice problem (org tickets)
- `ACCESS_ISSUE`: Access problem (org tickets)
- `PLAN_ISSUE`: Plan/subscription issue (org tickets)
- `OTHER`: Other issues

## API Endpoints

### Project Tickets

#### Create Project Ticket
```
POST /api/projects/{project_id}/tickets
Body: { title, description, ticket_type, priority }
Access: Clients and org members
```

#### Get Project Tickets
```
GET /api/projects/{project_id}/tickets
Access: Clients and org members
```

#### Get Project Ticket Details
```
GET /api/projects/{project_id}/tickets/{ticket_id}
Returns: Ticket with comments and attachments
Access: Clients and org members
```

#### Update Project Ticket
```
PATCH /api/projects/{project_id}/tickets/{ticket_id}
Body: { title?, description?, ticket_type?, status?, priority?, assigned_to? }
Access: Org members only (not clients)
```

#### Delete Project Ticket
```
DELETE /api/projects/{project_id}/tickets/{ticket_id}
Access: Org members only
```

#### Add Comment to Project Ticket
```
POST /api/projects/{project_id}/tickets/{ticket_id}/comments
Body: { comment, is_internal }
Access: Clients and org members
```

#### Add Attachment to Project Ticket
```
POST /api/projects/{project_id}/tickets/{ticket_id}/attachments
Body: { file_name, file_url, file_type, file_size }
Access: Clients and org members
```

### Organization Tickets

#### Create Org Ticket
```
POST /api/organizations/tickets
Body: { title, description, ticket_type, priority }
Access: Org owners and members
```

#### Get Org Tickets for Organization
```
GET /api/organizations/tickets
Access: Org owners and members
```

#### Get Org Ticket Details
```
GET /api/organizations/tickets/{ticket_id}
Returns: Ticket with comments and attachments
Access: Org members and admins
```

#### Update Org Ticket
```
PATCH /api/organizations/tickets/{ticket_id}
Body: { title?, description?, ticket_type?, status?, priority?, assigned_to? }
Access: Org members and admins
```

#### Delete Org Ticket
```
DELETE /api/organizations/tickets/{ticket_id}
Access: Org members and admins
```

#### Add Comment to Org Ticket
```
POST /api/organizations/tickets/{ticket_id}/comments
Body: { comment, is_internal }
Access: Org members and admins
```

#### Add Attachment to Org Ticket
```
POST /api/organizations/tickets/{ticket_id}/attachments
Body: { file_name, file_url, file_type, file_size }
Access: Org members and admins
```

### Admin Ticket Endpoints

#### Get All Org Tickets (Admin)
```
GET /api/admin/tickets
Access: Admins only
```

#### Get My Assigned Tickets (Admin)
```
GET /api/admin/tickets/assigned
Access: Admins only
```

#### Get Org Ticket (Admin View)
```
GET /api/admin/tickets/{ticket_id}
Access: Admins only
```

#### Update Org Ticket (Admin)
```
PATCH /api/admin/tickets/{ticket_id}
Access: Admins only
```

#### Add Comment (Admin)
```
POST /api/admin/tickets/{ticket_id}/comments
Access: Admins only
```

### My Tickets

#### Get My Assigned Project Tickets
```
GET /api/my-tickets/assigned
Access: Org members
```

## Access Control

### Project Tickets
- **Clients**: Can create, view, and comment on tickets for their projects
- **Org Members**: Can create, view, update, assign, and comment on tickets for their org's projects
- **Org Owners**: Same as org members

### Organization Tickets
- **Org Members/Owners**: Can create, view, update, and comment on their org's tickets
- **Admins**: Can view, update, assign, and comment on all org tickets

## Workflow

### Project Ticket Workflow

1. **Client raises ticket**:
   - Client identifies an issue (missing item, design change, correction)
   - Creates ticket with title, description, type, and priority
   - Ticket status: OPEN

2. **Org member reviews**:
   - Views ticket in project dashboard
   - Can assign to themselves or another team member
   - Updates status to IN_PROGRESS
   - Adds internal notes if needed

3. **Work on ticket**:
   - Assigned member works on the issue
   - Adds comments with updates
   - Can attach files (photos, documents)
   - Client can see progress and add comments

4. **Resolution**:
   - Member marks ticket as RESOLVED
   - Client reviews the resolution
   - If satisfied, ticket is CLOSED
   - If not satisfied, ticket is REOPENED

### Organization Ticket Workflow

1. **Org admin raises ticket**:
   - Identifies issue with app, invoice, plan, or access
   - Creates ticket with details
   - Ticket status: OPEN

2. **Super admin reviews**:
   - Views ticket in admin dashboard
   - Can assign to themselves
   - Updates status to IN_PROGRESS
   - Communicates with org admin via comments

3. **Resolution**:
   - Admin resolves the issue
   - Marks ticket as RESOLVED
   - Org admin confirms resolution
   - Ticket is CLOSED

## Notifications

Notifications are triggered for:
- New ticket created
- Ticket assigned to user
- Ticket status changed
- New comment added
- Ticket resolved
- Ticket reopened

Notifications are:
- Project-specific for project tickets
- Organization-specific for org tickets
- Visible in the notifications tab

## Frontend Implementation

### Components Needed

1. **TicketDashboard**: List view of all tickets with filters
2. **TicketCard**: Individual ticket display in list
3. **TicketDetailView**: Full ticket view with comments and attachments
4. **CreateTicketDialog**: Form to create new ticket
5. **UpdateTicketDialog**: Form to update ticket status/assignment
6. **CommentSection**: Display and add comments
7. **AttachmentSection**: Display and add attachments

### Integration Points

1. **Organization Dashboard**: Add "Support" tab
2. **Project Detail View**: Add "Tickets" section
3. **Admin Dashboard**: Add "Support Tickets" section
4. **Client Portal**: Add "Support" section for their project tickets

## Database Migration

Migration file: `6758abbdda8b_add_support_ticket_system_tables.py`

Tables created:
- `project_tickets`
- `org_tickets`
- `ticket_comments`
- `ticket_attachments`

Also includes:
- `support_tickets` (legacy, for backward compatibility)
- `admin_notifications`
- `recently_viewed_orgs`

## Testing

### Backend Testing
```bash
cd backend
poetry run fastapi dev app/main.py
# Visit http://localhost:8000/docs to test API endpoints
```

### Test Scenarios

1. **Project Ticket Creation**:
   - Login as client
   - Create ticket for their project
   - Verify ticket appears in project tickets list

2. **Ticket Assignment**:
   - Login as org member
   - View project tickets
   - Assign ticket to self
   - Verify assignment

3. **Comment Addition**:
   - Add comment to ticket
   - Verify comment appears
   - Test internal comments (not visible to clients)

4. **Status Updates**:
   - Update ticket status through workflow
   - Verify status changes

5. **Org Ticket Flow**:
   - Login as org admin
   - Create org ticket
   - Login as super admin
   - View and respond to ticket

## Future Enhancements

1. **Email Notifications**: Send email when tickets are created/updated
2. **File Upload**: Implement actual file upload (currently URL-based)
3. **Ticket Templates**: Pre-defined ticket templates for common issues
4. **SLA Tracking**: Track response and resolution times
5. **Ticket Analytics**: Dashboard showing ticket metrics
6. **Bulk Operations**: Bulk update/close tickets
7. **Ticket Search**: Advanced search and filtering
8. **Ticket Export**: Export tickets to CSV/PDF
9. **Ticket Linking**: Link related tickets
10. **Automated Workflows**: Auto-assign based on rules

## Implementation Status

### ✅ Completed
- Database models and migrations
- Repository layer
- Service layer with business logic
- API routes and endpoints
- Role-based access control
- Ticket lifecycle management
- Comments and attachments support

### 🚧 In Progress
- Frontend components
- Notification integration

### 📋 Pending
- End-to-end testing
- Documentation for frontend developers
- User guide for end users
