import { useState, useEffect } from 'react'
import './App.css'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Building2, Home, Users, Calendar, FileText, LogOut, Plus, Phone, Upload, DollarSign, UserPlus } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type UserRole = 'admin' | 'org_owner' | 'org_member' | 'client'

interface User {
  id: string
  email: string
  name: string
  role: UserRole
  org_id: string | null
  phone: string | null
}

interface Organization {
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

interface Project {
  id: string
  org_id: string
  name: string
  description: string
  status: string
  client_name: string
  budget: number
  start_date: string
}

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [user, setUser] = useState<User | null>(null)
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [mockOtp, setMockOtp] = useState('')

  useEffect(() => {
    if (token) {
      fetchUser()
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const res = await fetch(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await  res.json()
        setUser(data)
      } else {
        logout()
      }
    } catch (error) {
      console.error('Failed to fetch user', error)
      logout()
    }
  }

  const requestOtp = async () => {
    try {
      const res = await fetch(`${API_URL}/api/auth/phone/request-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone })
      })
      if (res.ok) {
        const data = await res.json()
        setMockOtp(data.otp)
        setOtpSent(true)
        alert(`Mock OTP sent: ${data.otp}`)
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to send OTP')
      }
    } catch (error) {
      console.error('Failed to request OTP', error)
      alert('Failed to send OTP')
    }
  }

  const verifyOtp = async () => {
    try {
      const res = await fetch(`${API_URL}/api/auth/phone/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, otp })
      })
      if (res.ok) {
        const data = await res.json()
        setToken(data.token)
        setUser(data.user)
        localStorage.setItem('token', data.token)
      } else {
        const error = await res.json()
        alert(error.detail || 'Invalid OTP')
      }
    } catch (error) {
      console.error('Failed to verify OTP', error)
      alert('Failed to verify OTP')
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    setPhone('')
    setOtp('')
    setOtpSent(false)
    setMockOtp('')
    localStorage.removeItem('token')
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-2 text-center">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mb-4">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-3xl font-bold">Interio Palette</CardTitle>
            <CardDescription className="text-base">
              Connect interior designers with homeowners
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!otpSent ? (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Phone Number</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      type="tel"
                      placeholder="Enter your phone number"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <p className="text-xs text-gray-500">
                    Demo phones: 9999999999 (admin), or any org member phone
                  </p>
                </div>
                <Button onClick={requestOtp} className="w-full" disabled={!phone}>
                  Send OTP
                </Button>
              </>
            ) : (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Enter OTP</label>
                  <Input
                    type="text"
                    placeholder="Enter 6-digit OTP"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    maxLength={6}
                  />
                  {mockOtp && (
                    <p className="text-xs text-green-600 font-medium">
                      Mock OTP: {mockOtp}
                    </p>
                  )}
                </div>
                <Button onClick={verifyOtp} className="w-full" disabled={!otp}>
                  Verify & Login
                </Button>
                <Button 
                  onClick={() => { setOtpSent(false); setOtp(''); setMockOtp(''); }} 
                  variant="outline" 
                  className="w-full"
                >
                  Change Phone Number
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  if (user.role === 'admin') {
    return <AdminDashboard user={user} token={token!} logout={logout} />
  } else if (user.role === 'org_owner' || user.role === 'org_member') {
    return <OrganizationDashboard user={user} token={token!} logout={logout} />
  } else if (user.role === 'client') {
    return <ClientDashboard user={user} token={token!} logout={logout} />
  }

  return null
}

function AdminDashboard({ user, token, logout }: { user: User; token: string; logout: () => void }) {
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [showAddOrg, setShowAddOrg] = useState(false)
  const [showAddMember, setShowAddMember] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    owner_email: '',
    owner_name: '',
    owner_phone: '',
    owner_password: '',
    subscription_plan: 'basic'
  })
  
  const [memberFormData, setMemberFormData] = useState({
    org_id: '',
    name: '',
    email: '',
    phone: '',
    password: '',
    role: 'org_member'
  })

  useEffect(() => {
    fetchOrganizations()
  }, [])

  const fetchOrganizations = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/organizations`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setOrganizations(data)
      }
    } catch (error) {
      console.error('Failed to fetch organizations', error)
    }
  }

  const createOrganization = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/organizations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })
      if (res.ok) {
        alert('Organization created successfully!')
        setShowAddOrg(false)
        setFormData({
          name: '',
          email: '',
          phone: '',
          address: '',
          city: '',
          state: '',
          pincode: '',
          owner_email: '',
          owner_name: '',
          owner_phone: '',
          owner_password: '',
          subscription_plan: 'basic'
        })
        fetchOrganizations()
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to create organization')
      }
    } catch (error) {
      console.error('Failed to create organization', error)
      alert('Failed to create organization')
    }
  }
  
  const handleAddOrgMember = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/organizations/${memberFormData.org_id}/members`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          name: memberFormData.name,
          email: memberFormData.email,
          phone: memberFormData.phone,
          password: memberFormData.password,
          role: memberFormData.role
        })
      })
      if (res.ok) {
        alert('Organization member added successfully!')
        setShowAddMember(false)
        setMemberFormData({ org_id: '', name: '', email: '', phone: '', password: '', role: 'org_member' })
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to add member')
      }
    } catch (error) {
      console.error('Failed to add member', error)
      alert('Failed to add member')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Interio Palette</h1>
              <p className="text-sm text-gray-500">Admin Dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium">{user.name}</span>
            <Button onClick={logout} variant="outline" size="sm">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Organizations</h2>
          <div className="flex gap-2">
            <Dialog open={showAddMember} onOpenChange={setShowAddMember}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <UserPlus className="w-4 h-4 mr-2" />
                  Add Member
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Add Organization Member</DialogTitle>
                  <DialogDescription>
                    Add a new member to an existing organization
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="member-org">Organization</Label>
                    <Select 
                      value={memberFormData.org_id} 
                      onValueChange={(value) => setMemberFormData({ ...memberFormData, org_id: value })}
                    >
                      <SelectTrigger id="member-org">
                        <SelectValue placeholder="Select organization" />
                      </SelectTrigger>
                      <SelectContent>
                        {organizations.map((org) => (
                          <SelectItem key={org.id} value={org.id}>
                            {org.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="member-name">Name</Label>
                    <Input
                      id="member-name"
                      placeholder="Member name"
                      value={memberFormData.name}
                      onChange={(e) => setMemberFormData({ ...memberFormData, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="member-email">Email</Label>
                    <Input
                      id="member-email"
                      type="email"
                      placeholder="member@example.com"
                      value={memberFormData.email}
                      onChange={(e) => setMemberFormData({ ...memberFormData, email: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="member-phone">Phone</Label>
                    <Input
                      id="member-phone"
                      type="tel"
                      placeholder="Phone number"
                      value={memberFormData.phone}
                      onChange={(e) => setMemberFormData({ ...memberFormData, phone: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="member-password">Password</Label>
                    <Input
                      id="member-password"
                      type="password"
                      placeholder="Temporary password"
                      value={memberFormData.password}
                      onChange={(e) => setMemberFormData({ ...memberFormData, password: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="member-role">Role</Label>
                    <Select 
                      value={memberFormData.role} 
                      onValueChange={(value) => setMemberFormData({ ...memberFormData, role: value })}
                    >
                      <SelectTrigger id="member-role">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="org_member">Member</SelectItem>
                        <SelectItem value="org_owner">Owner</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleAddOrgMember} className="flex-1">Add Member</Button>
                  <Button onClick={() => setShowAddMember(false)} variant="outline" className="flex-1">Cancel</Button>
                </div>
              </DialogContent>
            </Dialog>
            <Button onClick={() => setShowAddOrg(!showAddOrg)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Organization
            </Button>
          </div>
        </div>

        {showAddOrg && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Create New Organization</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Organization Name</label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Organization Email</label>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Organization Phone</label>
                  <Input
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">City</label>
                  <Input
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">State</label>
                  <Input
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Pincode</label>
                  <Input
                    value={formData.pincode}
                    onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                  />
                </div>
                <div className="col-span-2 space-y-2">
                  <label className="text-sm font-medium">Address</label>
                  <Input
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Owner Name</label>
                  <Input
                    value={formData.owner_name}
                    onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Owner Email</label>
                  <Input
                    type="email"
                    value={formData.owner_email}
                    onChange={(e) => setFormData({ ...formData, owner_email: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Owner Phone</label>
                  <Input
                    value={formData.owner_phone}
                    onChange={(e) => setFormData({ ...formData, owner_phone: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Owner Password</label>
                  <Input
                    type="password"
                    value={formData.owner_password}
                    onChange={(e) => setFormData({ ...formData, owner_password: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button onClick={createOrganization}>Create Organization</Button>
                <Button onClick={() => setShowAddOrg(false)} variant="outline">Cancel</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {organizations.map((org) => (
            <Card key={org.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">{org.name}</CardTitle>
                <CardDescription>{org.city}, {org.state}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Email:</span> {org.email}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Phone:</span> {org.phone}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Plan:</span> {org.subscription_plan}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    org.subscription_status === 'active' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {org.subscription_status}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {organizations.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center text-gray-500">
              No organizations yet. Click "Add Organization" to create one.
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}

function OrganizationDashboard({ user, token, logout }: { user: User; token: string; logout: () => void }) {
  const [activeTab, setActiveTab] = useState('projects')
  const [projects, setProjects] = useState<Project[]>([])
  const [clients, setClients] = useState<any[]>([])
  
  const [showAddClient, setShowAddClient] = useState(false)
  const [showAddProject, setShowAddProject] = useState(false)
  const [showAddTeamMember, setShowAddTeamMember] = useState(false)
  const [showAddEvent, setShowAddEvent] = useState(false)
  const [showUploadDesign, setShowUploadDesign] = useState(false)
  const [showCreateInvoice, setShowCreateInvoice] = useState(false)
  
  const [clientFormData, setClientFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    password: ''
  })
  
  const [projectFormData, setProjectFormData] = useState({
    client_id: '',
    name: '',
    description: '',
    budget: '',
    start_date: '',
    end_date: ''
  })
  
  const [teamMemberFormData, setTeamMemberFormData] = useState({
    project_id: '',
    name: '',
    email: '',
    phone: '',
    role: ''
  })
  
  const [eventFormData, setEventFormData] = useState({
    project_id: '',
    title: '',
    description: '',
    event_date: '',
    event_time: ''
  })
  
  const [designFormData, setDesignFormData] = useState({
    project_id: '',
    title: '',
    description: '',
    file: null as File | null
  })
  
  const [invoiceFormData, setInvoiceFormData] = useState({
    project_id: '',
    amount: '',
    due_date: '',
    description: '',
    items: ''
  })

  useEffect(() => {
    fetchProjects()
    fetchClients()
  }, [])

  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API_URL}/api/organizations/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setProjects(data)
      }
    } catch (error) {
      console.error('Failed to fetch projects', error)
    }
  }

  const fetchClients = async () => {
    try {
      const res = await fetch(`${API_URL}/api/organizations/clients`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setClients(data)
      }
    } catch (error) {
      console.error('Failed to fetch clients', error)
    }
  }
  
  const handleCreateClient = async () => {
    try {
      const res = await fetch(`${API_URL}/api/organizations/clients`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(clientFormData)
      })
      if (res.ok) {
        alert('Client created successfully!')
        setShowAddClient(false)
        setClientFormData({ name: '', email: '', phone: '', address: '', password: '' })
        fetchClients()
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to create client')
      }
    } catch (error) {
      console.error('Failed to create client', error)
      alert('Failed to create client')
    }
  }
  
  const handleCreateProject = async () => {
    try {
      const res = await fetch(`${API_URL}/api/organizations/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...projectFormData,
          budget: parseFloat(projectFormData.budget)
        })
      })
      if (res.ok) {
        alert('Project created successfully!')
        setShowAddProject(false)
        setProjectFormData({ client_id: '', name: '', description: '', budget: '', start_date: '', end_date: '' })
        fetchProjects()
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to create project')
      }
    } catch (error) {
      console.error('Failed to create project', error)
      alert('Failed to create project')
    }
  }
  
  const handleAddTeamMember = async () => {
    try {
      const res = await fetch(`${API_URL}/api/organizations/projects/${teamMemberFormData.project_id}/team`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          name: teamMemberFormData.name,
          email: teamMemberFormData.email,
          phone: teamMemberFormData.phone,
          role: teamMemberFormData.role
        })
      })
      if (res.ok) {
        alert('Team member added successfully!')
        setShowAddTeamMember(false)
        setTeamMemberFormData({ project_id: '', name: '', email: '', phone: '', role: '' })
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to add team member')
      }
    } catch (error) {
      console.error('Failed to add team member', error)
      alert('Failed to add team member')
    }
  }
  
  const handleCreateEvent = async () => {
    try {
      const res = await fetch(`${API_URL}/api/organizations/calendar/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(eventFormData)
      })
      if (res.ok) {
        alert('Event created successfully!')
        setShowAddEvent(false)
        setEventFormData({ project_id: '', title: '', description: '', event_date: '', event_time: '' })
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to create event')
      }
    } catch (error) {
      console.error('Failed to create event', error)
      alert('Failed to create event')
    }
  }
  
  const handleUploadDesign = async () => {
    try {
      const formData = new FormData()
      formData.append('project_id', designFormData.project_id)
      formData.append('title', designFormData.title)
      formData.append('description', designFormData.description)
      if (designFormData.file) {
        formData.append('file', designFormData.file)
      }
      
      const res = await fetch(`${API_URL}/api/organizations/designs`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      })
      if (res.ok) {
        alert('Design uploaded successfully!')
        setShowUploadDesign(false)
        setDesignFormData({ project_id: '', title: '', description: '', file: null })
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to upload design')
      }
    } catch (error) {
      console.error('Failed to upload design', error)
      alert('Failed to upload design')
    }
  }
  
  const handleCreateInvoice = async () => {
    try {
      const res = await fetch(`${API_URL}/api/organizations/invoices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...invoiceFormData,
          amount: parseFloat(invoiceFormData.amount)
        })
      })
      if (res.ok) {
        alert('Invoice created successfully!')
        setShowCreateInvoice(false)
        setInvoiceFormData({ project_id: '', amount: '', due_date: '', description: '', items: '' })
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to create invoice')
      }
    } catch (error) {
      console.error('Failed to create invoice', error)
      alert('Failed to create invoice')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Interio Palette</h1>
              <p className="text-sm text-gray-500">Organization Dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium">{user.name}</span>
            <Button onClick={logout} variant="outline" size="sm">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-4">
            <TabsTrigger value="projects">
              <Home className="w-4 h-4 mr-2" />
              Projects
            </TabsTrigger>
            <TabsTrigger value="clients">
              <Users className="w-4 h-4 mr-2" />
              Clients
            </TabsTrigger>
            <TabsTrigger value="calendar">
              <Calendar className="w-4 h-4 mr-2" />
              Calendar
            </TabsTrigger>
            <TabsTrigger value="invoices">
              <FileText className="w-4 h-4 mr-2" />
              Invoices
            </TabsTrigger>
          </TabsList>

          <TabsContent value="projects" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Projects</h2>
              <Dialog open={showAddProject} onOpenChange={setShowAddProject}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    New Project
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Create New Project</DialogTitle>
                    <DialogDescription>
                      Add a new project for your client
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="project-client">Client</Label>
                      <Select 
                        value={projectFormData.client_id} 
                        onValueChange={(value) => setProjectFormData({ ...projectFormData, client_id: value })}
                      >
                        <SelectTrigger id="project-client">
                          <SelectValue placeholder="Select a client" />
                        </SelectTrigger>
                        <SelectContent>
                          {clients.map((client) => (
                            <SelectItem key={client.id} value={client.id}>
                              {client.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="project-name">Project Name</Label>
                      <Input
                        id="project-name"
                        placeholder="Project name"
                        value={projectFormData.name}
                        onChange={(e) => setProjectFormData({ ...projectFormData, name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="project-description">Description</Label>
                      <Textarea
                        id="project-description"
                        placeholder="Project description"
                        value={projectFormData.description}
                        onChange={(e) => setProjectFormData({ ...projectFormData, description: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="project-budget">Budget (₹)</Label>
                      <Input
                        id="project-budget"
                        type="number"
                        placeholder="100000"
                        value={projectFormData.budget}
                        onChange={(e) => setProjectFormData({ ...projectFormData, budget: e.target.value })}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="project-start">Start Date</Label>
                        <Input
                          id="project-start"
                          type="date"
                          value={projectFormData.start_date}
                          onChange={(e) => setProjectFormData({ ...projectFormData, start_date: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="project-end">End Date</Label>
                        <Input
                          id="project-end"
                          type="date"
                          value={projectFormData.end_date}
                          onChange={(e) => setProjectFormData({ ...projectFormData, end_date: e.target.value })}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleCreateProject} className="flex-1">Create Project</Button>
                    <Button onClick={() => setShowAddProject(false)} variant="outline" className="flex-1">Cancel</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {projects.map((project) => (
                <Card key={project.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{project.name}</CardTitle>
                    <CardDescription>{project.client_name}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Budget:</span> ₹{project.budget.toLocaleString()}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Status:</span> {project.status}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Start:</span> {new Date(project.start_date).toLocaleDateString()}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            {projects.length === 0 && (
              <Card>
                <CardContent className="py-12 text-center text-gray-500">
                  No projects yet. Create clients first, then add projects.
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="clients" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Clients</h2>
              <Dialog open={showAddClient} onOpenChange={setShowAddClient}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Client
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle>Add New Client</DialogTitle>
                    <DialogDescription>
                      Create a new client account for your organization
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="client-name">Name</Label>
                      <Input
                        id="client-name"
                        placeholder="Client name"
                        value={clientFormData.name}
                        onChange={(e) => setClientFormData({ ...clientFormData, name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="client-email">Email</Label>
                      <Input
                        id="client-email"
                        type="email"
                        placeholder="client@example.com"
                        value={clientFormData.email}
                        onChange={(e) => setClientFormData({ ...clientFormData, email: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="client-phone">Phone</Label>
                      <Input
                        id="client-phone"
                        type="tel"
                        placeholder="Phone number"
                        value={clientFormData.phone}
                        onChange={(e) => setClientFormData({ ...clientFormData, phone: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="client-address">Address</Label>
                      <Textarea
                        id="client-address"
                        placeholder="Full address"
                        value={clientFormData.address}
                        onChange={(e) => setClientFormData({ ...clientFormData, address: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="client-password">Password</Label>
                      <Input
                        id="client-password"
                        type="password"
                        placeholder="Temporary password for client"
                        value={clientFormData.password}
                        onChange={(e) => setClientFormData({ ...clientFormData, password: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleCreateClient} className="flex-1">Create Client</Button>
                    <Button onClick={() => setShowAddClient(false)} variant="outline" className="flex-1">Cancel</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {clients.map((client) => (
                <Card key={client.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{client.name}</CardTitle>
                    <CardDescription>{client.email}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Phone:</span> {client.phone}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Address:</span> {client.address}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            {clients.length === 0 && (
              <Card>
                <CardContent className="py-12 text-center text-gray-500">
                  No clients yet. Click "Add Client" to create one.
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="calendar" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">Calendar & Team</h2>
              <div className="flex gap-2">
                <Dialog open={showAddTeamMember} onOpenChange={setShowAddTeamMember}>
                  <DialogTrigger asChild>
                    <Button variant="outline">
                      <UserPlus className="w-4 h-4 mr-2" />
                      Add Team Member
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                      <DialogTitle>Add Team Member</DialogTitle>
                      <DialogDescription>
                        Add a new team member to a project
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="team-project">Project</Label>
                        <Select 
                          value={teamMemberFormData.project_id} 
                          onValueChange={(value) => setTeamMemberFormData({ ...teamMemberFormData, project_id: value })}
                        >
                          <SelectTrigger id="team-project">
                            <SelectValue placeholder="Select a project" />
                          </SelectTrigger>
                          <SelectContent>
                            {projects.map((project) => (
                              <SelectItem key={project.id} value={project.id}>
                                {project.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="team-name">Name</Label>
                        <Input
                          id="team-name"
                          placeholder="Team member name"
                          value={teamMemberFormData.name}
                          onChange={(e) => setTeamMemberFormData({ ...teamMemberFormData, name: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="team-email">Email</Label>
                        <Input
                          id="team-email"
                          type="email"
                          placeholder="team@example.com"
                          value={teamMemberFormData.email}
                          onChange={(e) => setTeamMemberFormData({ ...teamMemberFormData, email: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="team-phone">Phone</Label>
                        <Input
                          id="team-phone"
                          type="tel"
                          placeholder="Phone number"
                          value={teamMemberFormData.phone}
                          onChange={(e) => setTeamMemberFormData({ ...teamMemberFormData, phone: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="team-role">Role</Label>
                        <Input
                          id="team-role"
                          placeholder="e.g., Designer, Contractor"
                          value={teamMemberFormData.role}
                          onChange={(e) => setTeamMemberFormData({ ...teamMemberFormData, role: e.target.value })}
                        />
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleAddTeamMember} className="flex-1">Add Member</Button>
                      <Button onClick={() => setShowAddTeamMember(false)} variant="outline" className="flex-1">Cancel</Button>
                    </div>
                  </DialogContent>
                </Dialog>
                
                <Dialog open={showAddEvent} onOpenChange={setShowAddEvent}>
                  <DialogTrigger asChild>
                    <Button>
                      <Calendar className="w-4 h-4 mr-2" />
                      Add Event
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                      <DialogTitle>Create Calendar Event</DialogTitle>
                      <DialogDescription>
                        Schedule a meeting or milestone
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="event-project">Project</Label>
                        <Select 
                          value={eventFormData.project_id} 
                          onValueChange={(value) => setEventFormData({ ...eventFormData, project_id: value })}
                        >
                          <SelectTrigger id="event-project">
                            <SelectValue placeholder="Select a project" />
                          </SelectTrigger>
                          <SelectContent>
                            {projects.map((project) => (
                              <SelectItem key={project.id} value={project.id}>
                                {project.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="event-title">Event Title</Label>
                        <Input
                          id="event-title"
                          placeholder="Client meeting"
                          value={eventFormData.title}
                          onChange={(e) => setEventFormData({ ...eventFormData, title: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="event-description">Description</Label>
                        <Textarea
                          id="event-description"
                          placeholder="Event details"
                          value={eventFormData.description}
                          onChange={(e) => setEventFormData({ ...eventFormData, description: e.target.value })}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="event-date">Date</Label>
                          <Input
                            id="event-date"
                            type="date"
                            value={eventFormData.event_date}
                            onChange={(e) => setEventFormData({ ...eventFormData, event_date: e.target.value })}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="event-time">Time</Label>
                          <Input
                            id="event-time"
                            type="time"
                            value={eventFormData.event_time}
                            onChange={(e) => setEventFormData({ ...eventFormData, event_time: e.target.value })}
                          />
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleCreateEvent} className="flex-1">Create Event</Button>
                      <Button onClick={() => setShowAddEvent(false)} variant="outline" className="flex-1">Cancel</Button>
                    </div>
                  </DialogContent>
                </Dialog>
                
                <Dialog open={showUploadDesign} onOpenChange={setShowUploadDesign}>
                  <DialogTrigger asChild>
                    <Button variant="outline">
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Design
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                      <DialogTitle>Upload Design</DialogTitle>
                      <DialogDescription>
                        Upload a design file for a project
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="design-project">Project</Label>
                        <Select 
                          value={designFormData.project_id} 
                          onValueChange={(value) => setDesignFormData({ ...designFormData, project_id: value })}
                        >
                          <SelectTrigger id="design-project">
                            <SelectValue placeholder="Select a project" />
                          </SelectTrigger>
                          <SelectContent>
                            {projects.map((project) => (
                              <SelectItem key={project.id} value={project.id}>
                                {project.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="design-title">Title</Label>
                        <Input
                          id="design-title"
                          placeholder="Design title"
                          value={designFormData.title}
                          onChange={(e) => setDesignFormData({ ...designFormData, title: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="design-description">Description</Label>
                        <Textarea
                          id="design-description"
                          placeholder="Design description"
                          value={designFormData.description}
                          onChange={(e) => setDesignFormData({ ...designFormData, description: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="design-file">File</Label>
                        <Input
                          id="design-file"
                          type="file"
                          accept="image/*,.pdf"
                          onChange={(e) => setDesignFormData({ ...designFormData, file: e.target.files?.[0] || null })}
                        />
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleUploadDesign} className="flex-1">Upload</Button>
                      <Button onClick={() => setShowUploadDesign(false)} variant="outline" className="flex-1">Cancel</Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </div>
            <Card>
              <CardContent className="py-12 text-center text-gray-500">
                Calendar events and team members will appear here...
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="invoices" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Invoices</h2>
              <Dialog open={showCreateInvoice} onOpenChange={setShowCreateInvoice}>
                <DialogTrigger asChild>
                  <Button>
                    <DollarSign className="w-4 h-4 mr-2" />
                    Create Invoice
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle>Create Invoice</DialogTitle>
                    <DialogDescription>
                      Generate an invoice for a project
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="invoice-project">Project</Label>
                      <Select 
                        value={invoiceFormData.project_id} 
                        onValueChange={(value) => setInvoiceFormData({ ...invoiceFormData, project_id: value })}
                      >
                        <SelectTrigger id="invoice-project">
                          <SelectValue placeholder="Select a project" />
                        </SelectTrigger>
                        <SelectContent>
                          {projects.map((project) => (
                            <SelectItem key={project.id} value={project.id}>
                              {project.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="invoice-amount">Amount (₹)</Label>
                      <Input
                        id="invoice-amount"
                        type="number"
                        placeholder="50000"
                        value={invoiceFormData.amount}
                        onChange={(e) => setInvoiceFormData({ ...invoiceFormData, amount: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="invoice-due">Due Date</Label>
                      <Input
                        id="invoice-due"
                        type="date"
                        value={invoiceFormData.due_date}
                        onChange={(e) => setInvoiceFormData({ ...invoiceFormData, due_date: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="invoice-description">Description</Label>
                      <Textarea
                        id="invoice-description"
                        placeholder="Invoice description"
                        value={invoiceFormData.description}
                        onChange={(e) => setInvoiceFormData({ ...invoiceFormData, description: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="invoice-items">Line Items (optional)</Label>
                      <Textarea
                        id="invoice-items"
                        placeholder="Item 1: ₹10000&#10;Item 2: ₹20000"
                        value={invoiceFormData.items}
                        onChange={(e) => setInvoiceFormData({ ...invoiceFormData, items: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleCreateInvoice} className="flex-1">Create Invoice</Button>
                    <Button onClick={() => setShowCreateInvoice(false)} variant="outline" className="flex-1">Cancel</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            <Card>
              <CardContent className="py-12 text-center text-gray-500">
                Invoices will appear here...
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

function ClientDashboard({ user, token, logout }: { user: User; token: string; logout: () => void }) {
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API_URL}/api/clients/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setProjects(data)
      }
    } catch (error) {
      console.error('Failed to fetch projects', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
              <Home className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Interio Palette</h1>
              <p className="text-sm text-gray-500">Client Portal</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium">{user.name}</span>
            <Button onClick={logout} variant="outline" size="sm">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold mb-6">My Projects</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">{project.name}</CardTitle>
                <CardDescription>{project.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Budget:</span> ₹{project.budget.toLocaleString()}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Status:</span> {project.status}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Start Date:</span> {new Date(project.start_date).toLocaleDateString()}
                </div>
                <Button className="w-full mt-4" variant="outline">View Details</Button>
              </CardContent>
            </Card>
          ))}
        </div>
        {projects.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center text-gray-500">
              No projects assigned yet. Your designer will create a project for you.
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}

export default App
