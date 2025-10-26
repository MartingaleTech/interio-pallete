import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Plus, FileText } from 'lucide-react'
import { Project } from '../../../../types'
import { projectService } from '../../../../services/projectService'

interface ProjectInvoicesProps {
  project: Project
  token: string
}

export function ProjectInvoices({ project, token }: ProjectInvoicesProps) {
  const [invoices, setInvoices] = useState<any[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState({
    amount: '',
    tax: '',
    due_date: ''
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchInvoices()
  }, [])

  const fetchInvoices = async () => {
    try {
      const data = await projectService.getProjectInvoices(token, project.id)
      setInvoices(data)
    } catch (error) {
      console.error('Failed to fetch invoices', error)
    }
  }

  const handleSubmit = async () => {
    if (!formData.amount || !formData.tax || !formData.due_date) {
      alert('Please fill all fields')
      return
    }

    setLoading(true)
    try {
      const total = parseFloat(formData.amount) + parseFloat(formData.tax)
      await projectService.createProjectInvoice(token, project.id, {
        amount: parseFloat(formData.amount),
        tax: parseFloat(formData.tax),
        total,
        due_date: formData.due_date
      })
      alert('Invoice created successfully!')
      setShowDialog(false)
      setFormData({ amount: '', tax: '', due_date: '' })
      fetchInvoices()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create invoice')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold mb-2">Invoices</h2>
          <p className="text-gray-600">Manage invoices for this project</p>
        </div>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Invoice
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Create New Invoice</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="amount">Amount (₹)</Label>
                <Input
                  id="amount"
                  type="number"
                  placeholder="100000"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tax">Tax (₹)</Label>
                <Input
                  id="tax"
                  type="number"
                  placeholder="18000"
                  value={formData.tax}
                  onChange={(e) => setFormData({ ...formData, tax: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="due_date">Due Date</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                />
              </div>
              {formData.amount && formData.tax && (
                <div className="p-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-600">Total Amount</p>
                  <p className="text-lg font-bold">₹{(parseFloat(formData.amount) + parseFloat(formData.tax)).toLocaleString()}</p>
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={loading}>
                {loading ? 'Creating...' : 'Create Invoice'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-4">
        {invoices.map((invoice) => (
          <Card key={invoice.id}>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="w-5 h-5" />
                {invoice.invoice_number}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p className="text-sm text-gray-500">Amount</p>
                  <p className="font-medium">₹{invoice.amount.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Tax</p>
                  <p className="font-medium">₹{invoice.tax.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Total</p>
                  <p className="font-medium text-lg">₹{invoice.total.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
                    invoice.payment_status === 'paid'
                      ? 'bg-green-100 text-green-700'
                      : invoice.payment_status === 'pending'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {invoice.payment_status}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Due Date</p>
                  <p className="font-medium">{new Date(invoice.due_date).toLocaleDateString()}</p>
                </div>
                {invoice.paid_date && (
                  <div>
                    <p className="text-sm text-gray-500">Paid Date</p>
                    <p className="font-medium">{new Date(invoice.paid_date).toLocaleDateString()}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {invoices.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No invoices yet. Create an invoice for this project.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
