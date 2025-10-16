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
  subscription_status: string
  subscription_plan: string
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
