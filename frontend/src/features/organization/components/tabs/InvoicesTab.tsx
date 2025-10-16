import { useState } from 'react'
import { Plus, DollarSign } from 'lucide-react'
import { TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useAuth } from '../../../../state/AuthContext'
import { organizationService } from '../../../../services/organizationService'
import { Project, InvoiceFormData } from '../../../../types'

interface InvoicesTabProps {
  projects: Project[]
}

export function InvoicesTab({ projects }: InvoicesTabProps) {
  const { token } = useAuth()
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState<InvoiceFormData>({
    project_id: '',
    amount: '',
    due_date: '',
    description: '',
    items: ''
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async () => {
    if (!token) return
    setIsLoading(true)
    try {
      await organizationService.createInvoice(token, formData)
      alert('Invoice created successfully!')
      setShowDialog(false)
      setFormData({ project_id: '', amount: '', due_date: '', description: '', items: '' })
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create invoice')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <TabsContent value="invoices" className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Invoices</h2>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Invoice
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Create Invoice</DialogTitle>
              <DialogDescription>
                Create a new invoice for a project
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="invoice-project">Project</Label>
                <Select 
                  value={formData.project_id} 
                  onValueChange={(value) => setFormData({ ...formData, project_id: value })}
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
                <div className="relative">
                  <DollarSign className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="invoice-amount"
                    type="number"
                    placeholder="100000"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="invoice-due-date">Due Date</Label>
                <Input
                  id="invoice-due-date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="invoice-description">Description</Label>
                <Textarea
                  id="invoice-description"
                  placeholder="Invoice description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="invoice-items">Items</Label>
                <Textarea
                  id="invoice-items"
                  placeholder="List of items/services"
                  value={formData.items}
                  onChange={(e) => setFormData({ ...formData, items: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Create Invoice'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      <p className="text-gray-500">Invoice list coming soon...</p>
    </TabsContent>
  )
}
