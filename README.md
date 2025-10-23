# Interio Palette

**Last Updated:** October 23, 2025

A multi-tenant SaaS platform connecting interior designers with homeowners in India.

---

## 📊 Project Status & Progress Tracking

### ✅ Completed Work

**Phase 0: Foundation & Database Integration** (Completed: Oct 16, 2025)

**Frontend Restructuring:**
- ✅ Modular component structure with src/ layout
- ✅ Feature-based organization (auth, admin, organization, client)
- ✅ Shared component library
- ✅ State management with Context API
- ✅ Service layer for API calls
- ✅ Custom hooks (useProjects, useClients)
- ✅ TypeScript type definitions

**Backend Restructuring:**
- ✅ Clean architecture with separation of concerns
- ✅ SQLAlchemy ORM with all entity models
- ✅ Repository pattern for data access
- ✅ Database-backed services (auth, org, project, client, invoice)
- ✅ Dependency injection for database sessions
- ✅ Alembic migrations setup
- ✅ SQLite (dev) / PostgreSQL-ready (production)
- ✅ Database initialization with default admin user
- ✅ Comprehensive documentation

**Testing & Validation:**
- ✅ Data persistence verified (vs old in-memory storage)
- ✅ Admin login working (email & phone OTP)
- ✅ Organization CRUD working
- ✅ Core API flows tested

### 🚧 Current Status

**Phase:** Phase 0 Complete → Ready for Phase 1

**Latest Work (Oct 16, 2025):**
- Database integration with SQLAlchemy
- Clean architecture implementation
- All routes updated with dependency injection
- Alembic migrations configured
- Documentation updated

### 📅 Roadmap & Priorities

**Phase 1: Core Features** (Next - Estimated 55-68 hours)

Priority order:
1. **File Attachments & 3D Design Upload** (15-18 hrs)
   - Upload system for project files (images, PDFs, 3D models)
   - Cloud storage integration
   - File metadata and permissions
   - Preview and download

2. **Comments/Notes on Attachments** (8-10 hrs)
   - Comment threads on files
   - @mentions for collaboration
   - Mark resolved/unresolved
   - Version tracking

3. **Support Ticket System** ✅ (Completed Oct 23, 2025)
   - Project-level tickets for client issues
   - Organization-level tickets for app/billing issues
   - Priority and category management
   - Assignment workflow
   - Status tracking and lifecycle management
   - Comment threads and attachments
   - Admin ticket management dashboard

4. **Real-time Chat** (20-25 hrs)
   - WebSocket integration
   - Project-level chat rooms
   - Direct messaging
   - Message history
   - Read receipts

**Phase 2: Integrations** (Estimated 30-35 hours)
- Real SMS/OTP provider (MSG91/Twilio)
- Payment gateway (Razorpay/Stripe)
- Email notifications
- Calendar reminders
- Push notifications

**Phase 3: Advanced Features** (Estimated 40-50 hours)
- Analytics dashboard
- Document e-signing
- 3D model viewer
- Automated workflows
- Mobile app (React Native)

### ⚠️ Known Issues & Technical Debt

**Backend:**
1. Old service files (`*_service.py`) need removal - new ones use `*_service_new.py`
2. No automated tests written yet (structure exists)
3. Using deprecated `datetime.utcnow()` 
4. SQLite limitation: Calendar attendees stored as JSON string

**Frontend:**
1. Testing infrastructure needs implementation
2. Error boundaries not fully implemented
3. Loading states need improvement

### 🎯 Next Session Planning

**Options for next work session:**
- [ ] **Option A:** Start Phase 1 - File attachment system
- [ ] **Option B:** Clean up technical debt (remove old files, add tests)
- [ ] **Option C:** User testing & feedback collection
- [ ] **Option D:** Continue with other Phase 1 features

**Recommendation:** Start with file attachments as it's foundational for comments and design sharing.

---

## Overview

Interio Palette is a comprehensive platform that enables:
- **Admin (Super Admin)** to manage interior design organizations
- **Organizations (Interior Designers)** to manage projects, clients, team members, and invoices
- **Clients (Homeowners)** to track their interior design projects in real-time

## Features

### Admin Dashboard
- Add and manage interior design organizations
- Manage organization members
- View and manage organization subscriptions
- Generate organization invoices
- Track all organizations and their status
- View and manage organization-level support tickets
- Assign and update ticket status

### Organization Dashboard
- Manage multiple projects
- Add and manage clients (homeowners)
- Assign team members to projects
- Schedule meetings and milestones via calendar
- Upload and share project designs
- Create and track project invoices
- Support ticket system for project issues and changes
- View and manage all project tickets

### Client Portal
- View assigned projects
- Track project progress
- View project designs and documents
- Access project calendar and milestones
- View invoices

## Architecture

### Multi-Tenant Design
Each interior design organization has its own isolated instance within the platform. Organizations can have multiple users (owner and members) and multiple projects, with each project linked to a client.

### Authentication
- Phone-based OTP authentication (currently mocked for development)
- Role-based access control (Admin, Org Owner, Org Member, Client)
- Secure token-based sessions

### Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Alembic (database migrations)
- Pydantic (data validation)
- bcrypt (password hashing)
- SQLite (development) / PostgreSQL (production-ready)

**Frontend:**
- React + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- shadcn/ui (UI components)
- Lucide Icons

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Poetry (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
poetry install
```

3. Initialize the database:
```bash
poetry run python -m src.core.init_db
```

This creates the database tables and a default admin user:
- Email: `admin@interiopalette.com`
- Password: `admin123`
- Phone: `9999999999`

4. Start the development server:
```bash
poetry run fastapi dev app/main.py
```

The backend will be available at `http://localhost:8000`

API documentation is available at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage Guide

### Admin Login

You can log in as admin using either:

**Email/Password:**
- Email: `admin@interiopalette.com`
- Password: `admin123`

**Phone OTP:**
- Phone: `9999999999`
- A mock OTP will be displayed after requesting it

### Creating an Organization
1. Log in as admin
2. Click "Add Organization"
3. Fill in the organization details and owner information
4. The owner will receive phone-based OTP login credentials

### Organization Owner Login
Use the phone number provided during organization creation to log in via OTP.

### Adding Clients
1. Log in as organization owner/member
2. Navigate to the "Clients" tab
3. Click "Add Client"
4. Provide client details including phone number
5. Clients can now log in using their phone number

### Managing Projects
1. Create clients first
2. Navigate to the "Projects" tab
3. Click "New Project"
4. Select a client and provide project details
5. Add team members, calendar events, designs, and invoices as needed

## API Endpoints

### Authentication
- `POST /api/auth/phone/request-otp` - Request OTP for phone number
- `POST /api/auth/phone/verify-otp` - Verify OTP and log in
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Log out

### Admin Endpoints
- `POST /api/admin/organizations` - Create organization
- `GET /api/admin/organizations` - List all organizations
- `GET /api/admin/organizations/{org_id}` - Get organization details
- `PATCH /api/admin/organizations/{org_id}` - Update organization
- `DELETE /api/admin/organizations/{org_id}` - Delete organization
- `GET /api/admin/organizations/{org_id}/members` - List organization members
- `POST /api/admin/organizations/{org_id}/members` - Add member
- `DELETE /api/admin/organizations/{org_id}/members/{user_id}` - Remove member
- `POST /api/admin/organizations/{org_id}/invoices` - Create org invoice
- `GET /api/admin/organizations/{org_id}/invoices` - List org invoices

### Organization Endpoints
- `POST /api/organizations/projects` - Create project
- `GET /api/organizations/projects` - List projects
- `GET /api/organizations/projects/{project_id}` - Get project details
- `POST /api/organizations/clients` - Add client
- `GET /api/organizations/clients` - List clients

### Project Endpoints
- `POST /api/projects/{project_id}/team` - Add team member
- `GET /api/projects/{project_id}/team` - List team members
- `POST /api/projects/{project_id}/calendar` - Create calendar event
- `GET /api/projects/{project_id}/calendar` - List calendar events
- `POST /api/projects/{project_id}/designs` - Upload design
- `GET /api/projects/{project_id}/designs` - List designs
- `POST /api/projects/{project_id}/invoices` - Create invoice
- `GET /api/projects/{project_id}/invoices` - List invoices

### Client Endpoints
- `GET /api/clients/projects` - List client's projects

### Ticket Endpoints
**Project Tickets:**
- `POST /api/projects/{project_id}/tickets` - Create project ticket
- `GET /api/projects/{project_id}/tickets` - List project tickets
- `GET /api/projects/{project_id}/tickets/{ticket_id}` - Get ticket details
- `PATCH /api/projects/{project_id}/tickets/{ticket_id}` - Update ticket
- `DELETE /api/projects/{project_id}/tickets/{ticket_id}` - Delete ticket
- `POST /api/projects/{project_id}/tickets/{ticket_id}/comments` - Add comment
- `POST /api/projects/{project_id}/tickets/{ticket_id}/attachments` - Add attachment

**Organization Tickets:**
- `POST /api/organizations/tickets` - Create org ticket
- `GET /api/organizations/tickets` - List org tickets
- `GET /api/organizations/tickets/{ticket_id}` - Get ticket details
- `PATCH /api/organizations/tickets/{ticket_id}` - Update ticket
- `DELETE /api/organizations/tickets/{ticket_id}` - Delete ticket
- `POST /api/organizations/tickets/{ticket_id}/comments` - Add comment
- `POST /api/organizations/tickets/{ticket_id}/attachments` - Add attachment

**Admin Ticket Management:**
- `GET /api/admin/tickets` - List all org tickets
- `GET /api/admin/tickets/{ticket_id}` - Get ticket details
- `PATCH /api/admin/tickets/{ticket_id}` - Update ticket status/assignment
- `POST /api/admin/tickets/{ticket_id}/comments` - Add admin comment

**My Tickets:**
- `GET /api/my-tickets/assigned` - Get my assigned tickets (project + org)
- `GET /api/my-tickets/projects/assigned` - Get my assigned project tickets

## Data Models

### User
- id, email, name, role, org_id, phone, created_at

### Organization
- id, name, email, phone, address, city, state, pincode
- owner_id, subscription_status, subscription_plan
- subscription_start, subscription_end, created_at

### Project
- id, org_id, name, description, status
- client_id, client_name, budget
- start_date, end_date, created_at

### Client
- id, org_id, name, email, phone, address, created_at

### Team Member
- id, project_id, user_id, name, role

### Calendar Event
- id, project_id, title, description, event_type
- start_time, end_time, attendees, created_at

### Project Design
- id, project_id, title, description
- file_url, file_type, uploaded_by, uploaded_at

### Invoice
- id, project_id, org_id, invoice_number
- amount, tax, total, payment_status
- due_date, paid_date, created_at

### Project Ticket
- id, project_id, org_id, created_by, assigned_to
- title, description, ticket_type, status, priority
- created_at, updated_at, resolved_at

### Organization Ticket
- id, org_id, created_by, assigned_to
- title, description, ticket_type, status, priority
- created_at, updated_at, resolved_at

### Ticket Comment
- id, project_ticket_id/org_ticket_id, user_id
- comment, is_internal
- created_at, updated_at

### Ticket Attachment
- id, project_ticket_id/org_ticket_id, uploaded_by
- file_name, file_url, file_type, file_size
- created_at

## Development Notes

### Database
The platform uses SQLAlchemy ORM with SQLite for development and is production-ready for PostgreSQL:
- **Development**: SQLite database (`interio_palette.db`)
- **Data Persistence**: All data persists across server restarts
- **Migrations**: Alembic manages schema changes
- **Production**: Set `DATABASE_URL` environment variable to PostgreSQL connection string

**Switch to PostgreSQL:**
```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
poetry run alembic upgrade head
```

### Mock OTP
The OTP system is mocked for development. The OTP is:
- Printed to the backend console
- Returned in the API response (for demo purposes)
- Valid for 10 minutes

For production, integrate with SMS providers like:
- Twilio
- AWS SNS
- Firebase Auth
- MSG91 (popular in India)

### File Uploads
File upload functionality is planned but not yet implemented. For production:
- Use cloud storage (AWS S3, Google Cloud Storage, Azure Blob)
- Implement file validation and security
- Add support for images, PDFs, 3D models

### Payment Integration
Payment processing placeholders are included. For production, integrate with:
- Razorpay (popular in India)
- Stripe
- PayU
- Paytm

## Future Enhancements

### Phase 1 (In Progress)
- File upload and storage system for project designs
- Comment/notes system for attachments
- ✅ Support ticket system (Completed Oct 23, 2025)
  - Two-level ticketing: project-level and org-level
  - Full lifecycle management with status tracking
  - Comments and attachments support
  - Assignment and priority management
  - Admin dashboard for ticket management
- Real-time chat between designers and clients

### Phase 2
- Real SMS/OTP provider integration (MSG91, Twilio)
- Payment gateway integration (Razorpay, Stripe)
- Advanced calendar with reminders and notifications
- Real-time notifications (WebSocket)

### Phase 3
- Mobile app (React Native)
- Analytics and reporting dashboard
- Document e-signing
- 3D design viewer
- Automated workflow and approval system

## Security Considerations

- All passwords are hashed using bcrypt
- Token-based authentication
- Role-based access control
- CORS enabled for development (restrict in production)
- Environment variables for sensitive data
- Input validation using Pydantic

## Deployment

### Backend Deployment
The backend can be deployed to:
- Fly.io (recommended)
- Heroku
- AWS EC2
- Google Cloud Run
- Railway

Make sure to:
- Set up environment variables
- Use a proper database (PostgreSQL)
- Enable HTTPS
- Configure CORS properly
- Set up monitoring

### Frontend Deployment
The frontend can be deployed to:
- Vercel (recommended)
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

Make sure to:
- Update VITE_API_URL environment variable
- Build the production bundle
- Enable HTTPS
- Configure caching

## License

Proprietary - All rights reserved

## Support

For questions or support, contact: [Your contact information]

## Credits

Developed by Devin for Melugiri Deepak (@deepakmelugiri)
