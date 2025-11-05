import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft, MessageSquare } from 'lucide-react'
import { adminService, SupportTicket } from '../../../services/adminService'
import { Organization } from '../../../types'

interface OrgDashboardProps {
  orgId: string
  token: string
  onBack: () => void
}

export function OrgDashboard({ orgId, token, onBack }: OrgDashboardProps) {
  const [org, setOrg] = useState<Organization | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'invoices' | 'tickets' | 'contact'>('overview')
  const [invoices, setInvoices] = useState<any[]>([])
  const [tickets, setTickets] = useState<SupportTicket[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOrgData()
    adminService.recordOrgView(token, orgId).catch(console.error)
  }, [orgId, token])

  const fetchOrgData = async () => {
    try {
      setLoading(true)
      const [orgData, invoicesData, ticketsData] = await Promise.all([
        adminService.getOrganization(token, orgId),
        adminService.getOrgInvoices(token, orgId),
        adminService.getOrgTickets(token, orgId)
      ])
      
      setOrg(orgData)
      setInvoices(invoicesData)
      setTickets(ticketsData)
    } catch (error) {
      console.error('Failed to fetch org data', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTicketStatusChange = async (ticketId: string, newStatus: string) => {
    try {
      await adminService.updateTicket(token, ticketId, { status: newStatus })
      fetchOrgData()
    } catch (error) {
      console.error('Failed to update ticket', error)
    }
  }

  if (loading || !org) {
    return <div className="p-8">Loading...</div>
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{org.name}</h1>
          <p className="text-gray-500 mt-1">{org.city}, {org.state}</p>
        </div>
      </div>

      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'overview'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('invoices')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'invoices'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Invoices
        </button>
        <button
          onClick={() => setActiveTab('tickets')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'tickets'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Support Tickets
        </button>
        <button
          onClick={() => setActiveTab('contact')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'contact'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Contact
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Organization Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="font-medium">{org.email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Phone</p>
                  <p className="font-medium">{org.phone}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Address</p>
                  <p className="font-medium">{org.address}</p>
                  <p className="text-sm">{org.city}, {org.state} - {org.pincode}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Subscription Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Plan</p>
                  <p className="font-medium text-lg">{org.subscription_plan}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <span className={`inline-block px-3 py-1 rounded text-sm font-medium ${
                    org.subscription_status === 'active' 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {org.subscription_status}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Subscription Period</p>
                  <p className="text-sm">
                    {org.subscription_start && org.subscription_end 
                      ? `${new Date(org.subscription_start).toLocaleDateString()} - ${new Date(org.subscription_end).toLocaleDateString()}`
                      : 'Not set'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'invoices' && (
        <Card>
          <CardHeader>
            <CardTitle>Organization Invoices</CardTitle>
            <CardDescription>Subscription billing history</CardDescription>
          </CardHeader>
          <CardContent>
            {invoices.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No invoices yet</p>
            ) : (
              <div className="space-y-3">
                {invoices.map((invoice) => (
                  <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">{invoice.invoice_number}</p>
                      <p className="text-sm text-gray-500">
                        {invoice.billing_period_start} - {invoice.billing_period_end}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">₹{invoice.amount.toLocaleString()}</p>
                      <span className={`text-xs px-2 py-1 rounded ${
                        invoice.payment_status === 'paid'
                          ? 'bg-green-100 text-green-700'
                          : invoice.payment_status === 'pending'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {invoice.payment_status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'tickets' && (
        <Card>
          <CardHeader>
            <CardTitle>Support Tickets</CardTitle>
            <CardDescription>Tickets raised by this organization</CardDescription>
          </CardHeader>
          <CardContent>
            {tickets.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No support tickets</p>
            ) : (
              <div className="space-y-3">
                {tickets.map((ticket) => (
                  <div key={ticket.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="font-medium">{ticket.subject}</p>
                        <p className="text-sm text-gray-500 mt-1">{ticket.description}</p>
                      </div>
                      <div className="flex gap-2">
                        <span className={`text-xs px-2 py-1 rounded ${
                          ticket.priority === 'high'
                            ? 'bg-red-100 text-red-700'
                            : ticket.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}>
                          {ticket.priority}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          ticket.status === 'open'
                            ? 'bg-green-100 text-green-700'
                            : ticket.status === 'in_progress'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                          {ticket.status}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2 mt-3">
                      {ticket.status === 'open' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleTicketStatusChange(ticket.id, 'in_progress')}
                        >
                          Mark In Progress
                        </Button>
                      )}
                      {ticket.status === 'in_progress' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleTicketStatusChange(ticket.id, 'resolved')}
                        >
                          Mark Resolved
                        </Button>
                      )}
                    </div>
                    <p className="text-xs text-gray-400 mt-2">
                      Created: {new Date(ticket.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'contact' && (
        <Card>
          <CardHeader>
            <CardTitle>Contact Organization</CardTitle>
            <CardDescription>Chat with organization owners (Coming Soon)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">
              <MessageSquare className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 mb-2">Chat functionality will be available in Phase 1</p>
              <p className="text-sm text-gray-400">
                You'll be able to communicate directly with organization owners here
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
