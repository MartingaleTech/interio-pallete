import { useState } from 'react'
import { Plus } from 'lucide-react'
import { TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useAuth } from '../../../../state/AuthContext'
import { organizationService } from '../../../../services/organizationService'
import { Client, ClientFormData } from '../../../../types'

interface ClientsTabProps {
  clients: Client[]
  onRefresh: () => void
}

export function ClientsTab({ clients, onRefresh }: ClientsTabProps) {
  const { token } = useAuth()
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState<ClientFormData>({
    name: '',
    email: '',
    phone: '',
    address: '',
    password: ''
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      await organizationService.createClient(token, formData)
      alert('Client created successfully!')
      setShowDialog(false)
      setFormData({ name: '', email: '', phone: '', address: '', password: '' })
      onRefresh()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create client')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <TabsContent value="clients" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Clients</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
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
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="client-email">Email</Label>
                <Input
                  id="client-email"
                  type="email"
                  placeholder="client@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="client-phone">Phone</Label>
                <Input
                  id="client-phone"
                  type="tel"
                  placeholder="Phone number"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="client-address">Address</Label>
                <Textarea
                  id="client-address"
                  placeholder="Full address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="client-password">Password</Label>
                <Input
                  id="client-password"
                  type="password"
                  placeholder="Temporary password for client"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Create Client'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
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
  )
}
