import { useEffect, useState } from 'react'
import { useAuth } from '../../../state/AuthContext'
import { chatService } from '../../../services/chatService'
import { Card } from '../../../components/ui/card'
import { Badge } from '../../../components/ui/badge'
import { ScrollArea } from '../../../components/ui/scroll-area'
import { User } from 'lucide-react'

interface DirectMessagesProps {
  onConversationSelect: (userId: string, userName: string) => void
  currentDirectUserId: string | null
}

interface OrgMember {
  id: string
  name: string
  email: string
  role: string
}

export function DirectMessages({ onConversationSelect, currentDirectUserId }: DirectMessagesProps) {
  const { token } = useAuth()
  const [orgMembers, setOrgMembers] = useState<OrgMember[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadOrgMembers()
  }, [token])

  const loadOrgMembers = async () => {
    if (!token) return
    try {
      setLoading(true)
      const members = await chatService.getOrgMembers(token)
      setOrgMembers(members)
    } catch (error) {
      console.error('Failed to load org members:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Direct Messages</h2>
        <p className="text-xs text-muted-foreground mt-1">
          Message anyone in your organization
        </p>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-2">
          {loading ? (
            <div className="text-center text-muted-foreground py-8">
              Loading members...
            </div>
          ) : orgMembers.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No other members in your organization
            </div>
          ) : (
            orgMembers.map((member) => (
              <Card
                key={member.id}
                className={`p-3 cursor-pointer hover:bg-accent transition-colors ${
                  currentDirectUserId === member.id ? 'bg-accent' : ''
                }`}
                onClick={() => onConversationSelect(member.id, member.name)}
              >
                <div className="flex items-start gap-3">
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <User className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium truncate">{member.name}</h3>
                      <Badge variant="outline" className="text-xs">
                        {member.role}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground truncate mt-1">
                      {member.email}
                    </p>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
