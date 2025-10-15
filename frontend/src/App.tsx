import { useState, useEffect } from 'react'
import './App.css'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Building2, Home, Users, Calendar, FileText, LogOut, Plus, Phone } from 'lucide-react'

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
          <Button onClick={() => setShowAddOrg(!showAddOrg)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Organization
          </Button>
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
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Project
              </Button>
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
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Client
              </Button>
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

          <TabsContent value="calendar">
            <Card>
              <CardHeader>
                <CardTitle>Calendar</CardTitle>
                <CardDescription>Schedule meetings and project milestones</CardDescription>
              </CardHeader>
              <CardContent className="py-12 text-center text-gray-500">
                Calendar functionality coming soon...
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="invoices">
            <Card>
              <CardHeader>
                <CardTitle>Invoices</CardTitle>
                <CardDescription>Manage project invoices and payments</CardDescription>
              </CardHeader>
              <CardContent className="py-12 text-center text-gray-500">
                Invoice management coming soon...
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
