import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { adminService, SupportTicket } from '../../../services/adminService'

interface AdminTicketsProps {
  token: string
}

export function AdminTickets({ token }: AdminTicketsProps) {
  const [tickets, setTickets] = useState<SupportTicket[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'open' | 'in_progress' | 'resolved'>('all')

  useEffect(() => {
    fetchTickets()
  }, [token])

  const fetchTickets = async () => {
    try {
      setLoading(true)
      const data = await adminService.getAllTickets(token)
      setTickets(data)
    } catch (error) {
      console.error('Failed to fetch tickets', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (ticketId: string, newStatus: string) => {
    try {
      await adminService.updateTicket(token, ticketId, { status: newStatus })
      fetchTickets()
    } catch (error) {
      console.error('Failed to update ticket', error)
    }
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
        <h1 className="text-3xl font-bold">Support Tickets</h1>
        <p className="text-gray-500 mt-1">Manage support requests from organizations</p>
      </div>

      <div className="flex gap-2">
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
      </div>

      <div className="space-y-4">
        {filteredTickets.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-gray-500">
              No {filter !== 'all' ? filter : ''} tickets found
            </CardContent>
          </Card>
        ) : (
          filteredTickets.map((ticket) => (
            <Card key={ticket.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{ticket.subject}</CardTitle>
                    <CardDescription className="mt-2">{ticket.description}</CardDescription>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <span className={`text-xs px-2 py-1 rounded whitespace-nowrap ${
                      ticket.priority === 'high'
                        ? 'bg-red-100 text-red-700'
                        : ticket.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-blue-100 text-blue-700'
                    }`}>
                      {ticket.priority}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded whitespace-nowrap ${
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
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    Created: {new Date(ticket.created_at).toLocaleString()}
                  </div>
                  <div className="flex gap-2">
                    {ticket.status === 'open' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleStatusChange(ticket.id, 'in_progress')}
                      >
                        Start Working
                      </Button>
                    )}
                    {ticket.status === 'in_progress' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleStatusChange(ticket.id, 'resolved')}
                      >
                        Mark Resolved
                      </Button>
                    )}
                    {ticket.status === 'resolved' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleStatusChange(ticket.id, 'open')}
                      >
                        Reopen
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
