import { useState, useEffect } from 'react'
import { AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ticketService } from '../../../services/ticketService'
import { OrgTicket, TicketStatus, TicketPriority, TicketType } from '../../../types'

interface AdminTicketsProps {
  token: string
}

const ticketTypeLabels: Record<TicketType, string> = {
  project_issue: 'Project Issue',
  design_change: 'Design Change',
  correction: 'Correction',
  missing_item: 'Missing Item',
  interior_work: 'Interior Work',
  app_issue: 'App Issue',
  invoice_issue: 'Invoice Issue',
  access_issue: 'Access Issue',
  plan_issue: 'Plan Issue',
  other: 'Other'
}

const priorityColors: Record<TicketPriority, string> = {
  low: 'bg-gray-500',
  medium: 'bg-blue-500',
  high: 'bg-orange-500',
  urgent: 'bg-red-500'
}

const statusIcons: Record<TicketStatus, any> = {
  open: AlertCircle,
  in_progress: Clock,
  resolved: CheckCircle,
  closed: CheckCircle,
  reopened: AlertCircle
}

export function AdminTickets({ token }: AdminTicketsProps) {
  const [tickets, setTickets] = useState<OrgTicket[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'open' | 'in_progress' | 'resolved' | 'closed'>('all')

  useEffect(() => {
    fetchTickets()
  }, [token])

  const fetchTickets = async () => {
    try {
      setLoading(true)
      const data = await ticketService.getAllOrgTickets(token)
      setTickets(data)
    } catch (error) {
      console.error('Failed to fetch tickets', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (ticketId: string, newStatus: TicketStatus) => {
    try {
      await ticketService.updateOrgTicketAdmin(token, ticketId, { status: newStatus })
      fetchTickets()
    } catch (error) {
      console.error('Failed to update ticket', error)
    }
  }

  const StatusIcon = ({ status }: { status: TicketStatus }) => {
    const Icon = statusIcons[status]
    return <Icon className="w-4 h-4" />
  }

  const filteredTickets = filter === 'all' 
    ? tickets 
    : tickets.filter(t => t.status === filter)

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Organization Support Tickets</h1>
        <p className="text-gray-500 mt-1">Manage support requests from organizations</p>
      </div>

      <div className="flex gap-2 flex-wrap">
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          onClick={() => setFilter('all')}
        >
          All ({tickets.length})
        </Button>
        <Button
          variant={filter === 'open' ? 'default' : 'outline'}
          onClick={() => setFilter('open')}
        >
          Open ({tickets.filter(t => t.status === 'open').length})
        </Button>
        <Button
          variant={filter === 'in_progress' ? 'default' : 'outline'}
          onClick={() => setFilter('in_progress')}
        >
          In Progress ({tickets.filter(t => t.status === 'in_progress').length})
        </Button>
        <Button
          variant={filter === 'resolved' ? 'default' : 'outline'}
          onClick={() => setFilter('resolved')}
        >
          Resolved ({tickets.filter(t => t.status === 'resolved').length})
        </Button>
        <Button
          variant={filter === 'closed' ? 'default' : 'outline'}
          onClick={() => setFilter('closed')}
        >
          Closed ({tickets.filter(t => t.status === 'closed').length})
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredTickets.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="py-12 text-center text-gray-500">
              No {filter !== 'all' ? filter : ''} tickets found
            </CardContent>
          </Card>
        ) : (
          filteredTickets.map((ticket) => (
            <Card key={ticket.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{ticket.title}</CardTitle>
                    <CardDescription className="mt-1">
                      {ticket.org_name || 'Unknown Organization'}
                    </CardDescription>
                  </div>
                  <Badge className={priorityColors[ticket.priority]}>
                    {ticket.priority}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <StatusIcon status={ticket.status} />
                  <span className="font-medium capitalize">{ticket.status.replace('_', ' ')}</span>
                </div>
                <div className="text-sm">
                  <span className="font-medium">Type:</span> {ticketTypeLabels[ticket.ticket_type]}
                </div>
                <div className="text-sm text-gray-600 line-clamp-2">
                  {ticket.description}
                </div>
                {ticket.creator_name && (
                  <div className="text-sm">
                    <span className="font-medium">Created by:</span> {ticket.creator_name}
                  </div>
                )}
                {ticket.assignee_name && (
                  <div className="text-sm">
                    <span className="font-medium">Assigned to:</span> {ticket.assignee_name}
                  </div>
                )}
                <div className="text-xs text-gray-500">
                  Created {new Date(ticket.created_at).toLocaleDateString()}
                </div>
                <div className="flex gap-2 pt-2">
                  {ticket.status === 'open' && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleStatusChange(ticket.id, 'in_progress')}
                    >
                      Start Working
                    </Button>
                  )}
                  {ticket.status === 'in_progress' && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleStatusChange(ticket.id, 'resolved')}
                    >
                      Mark Resolved
                    </Button>
                  )}
                  {ticket.status === 'resolved' && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleStatusChange(ticket.id, 'closed')}
                      >
                        Close
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleStatusChange(ticket.id, 'reopened')}
                      >
                        Reopen
                      </Button>
                    </>
                  )}
                  {ticket.status === 'closed' && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleStatusChange(ticket.id, 'reopened')}
                    >
                      Reopen
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
