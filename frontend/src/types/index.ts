export type UserRole = 'admin' | 'org_owner' | 'org_member' | 'client'

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  org_id: string | null
  phone: string | null
}

export interface Organization {
  id: string
  name: string
  email: string
  phone: string
  address: string
  city: string
  state: string
  pincode: string
  owner_id: string
  subscription_status: string
  subscription_plan: string
  subscription_start: string | null
  subscription_end: string | null
  created_at: string | null
}

export interface Project {
  id: string
  org_id: string
  name: string
  description: string
  status: string
  client_name: string
  budget: number
  start_date: string
  end_date?: string
}

export interface Client {
  id: string
  name: string
  email: string
  phone: string
  address: string
  org_id: string
}

export interface TeamMember {
  id: string
  first_name?: string
  last_name?: string
  name?: string
  email: string
  phone?: string
  role: string
  org_id?: string
  project_id?: string
}

export interface Event {
  id: string
  project_id: string
  title: string
  description: string
  event_date: string
  event_time: string
}

export interface Design {
  id: string
  project_id: string
  title: string
  description: string
  file_url: string
  created_at: string
}

export interface Invoice {
  id: string
  project_id: string
  amount: number
  due_date: string
  description: string
  items: string
  status: string
  created_at: string
}

export interface OrganizationFormData {
  name: string
  email: string
  phone: string
  address: string
  city: string
  state: string
  pincode: string
  owner_email: string
  owner_name: string
  owner_phone: string
  owner_password: string
  subscription_plan: string
}

export interface MemberFormData {
  org_id: string
  name: string
  email: string
  phone: string
  password: string
  role: string
}

export interface ClientFormData {
  name: string
  email: string
  phone: string
  address: string
  password: string
}

export interface ProjectFormData {
  client_id: string
  name: string
  description: string
  budget: string
  start_date: string
  end_date: string
}

export interface TeamMemberFormData {
  project_id: string
  name: string
  email: string
  phone: string
  role: string
}

export interface EventFormData {
  project_id: string
  title: string
  description: string
  event_date: string
  event_time: string
}

export interface DesignFormData {
  project_id: string
  title: string
  description: string
  file: File | null
}

export interface InvoiceFormData {
  project_id: string
  amount: string
  due_date: string
  description: string
  items: string
}

export interface OrgTeamMemberFormData {
  first_name: string
  last_name: string
  email: string
  phone: string
  role: string
  password: string
}

export type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed' | 'reopened'
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent'
export type TicketType = 
  | 'project_issue'
  | 'design_change'
  | 'correction'
  | 'missing_item'
  | 'interior_work'
  | 'app_issue'
  | 'invoice_issue'
  | 'access_issue'
  | 'plan_issue'
  | 'other'

export interface ProjectTicket {
  id: string
  project_id: string
  org_id: string
  created_by: string
  assigned_to: string | null
  title: string
  description: string
  ticket_type: TicketType
  status: TicketStatus
  priority: TicketPriority
  created_at: string
  updated_at: string
  resolved_at: string | null
  creator_name?: string
  assignee_name?: string
}

export interface OrgTicket {
  id: string
  org_id: string
  created_by: string
  assigned_to: string | null
  title: string
  description: string
  ticket_type: TicketType
  status: TicketStatus
  priority: TicketPriority
  created_at: string
  updated_at: string
  resolved_at: string | null
  creator_name?: string
  assignee_name?: string
  org_name?: string
}

export interface TicketComment {
  id: string
  project_ticket_id?: string
  org_ticket_id?: string
  user_id: string
  comment: string
  is_internal: boolean
  created_at: string
  updated_at: string
  user_name?: string
}

export interface TicketAttachment {
  id: string
  project_ticket_id?: string
  org_ticket_id?: string
  uploaded_by: string
  file_name: string
  file_url: string
  file_type: string
  file_size: number
  created_at: string
  uploader_name?: string
}

export interface ProjectTicketWithDetails extends ProjectTicket {
  comments: TicketComment[]
  attachments: TicketAttachment[]
}

export interface OrgTicketWithDetails extends OrgTicket {
  comments: TicketComment[]
  attachments: TicketAttachment[]
}

export interface ProjectTicketFormData {
  title: string
  description: string
  ticket_type: TicketType
  priority: TicketPriority
}

export interface OrgTicketFormData {
  title: string
  description: string
  ticket_type: TicketType
  priority: TicketPriority
}

export interface TicketCommentFormData {
  comment: string
  is_internal: boolean
}

export interface TicketAttachmentFormData {
  file_name: string
  file_url: string
  file_type: string
  file_size: number
}

export interface ProjectNotification {
  id: string
  project_id: string
  org_id: string
  user_id?: string
  notification_type: string
  title: string
  message: string
  is_read: boolean
  created_at: string
}

export interface ProjectNotificationFormData {
  notification_type: string
  title: string
  message: string
  user_id?: string
}

export interface ProjectDailyUpdate {
  id: string
  project_id: string
  org_id: string
  user_id: string
  user_name: string
  update_text: string
  attachments?: string
  created_at: string
  updated_at: string
}

export interface ProjectDailyUpdateFormData {
  update_text: string
  attachments?: string
}
