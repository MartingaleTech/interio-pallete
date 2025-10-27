import { useEffect } from 'react'
import { useChat } from '../../../state/ChatContext'
import { Card } from '../../../components/ui/card'
import { Badge } from '../../../components/ui/badge'
import { ScrollArea } from '../../../components/ui/scroll-area'

interface DirectMessagesProps {
  onConversationSelect: (userId: string, userName: string) => void
}

export function DirectMessages({ onConversationSelect }: DirectMessagesProps) {
  const { directConversations, currentDirectUserId, loadDirectConversations } = useChat()

  useEffect(() => {
    loadDirectConversations()
  }, [loadDirectConversations])

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Direct Messages</h2>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-2">
          {directConversations.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No direct messages
            </div>
          ) : (
            directConversations.map((conversation) => (
              <Card
                key={conversation.user_id}
                className={`p-3 cursor-pointer hover:bg-accent transition-colors ${
                  currentDirectUserId === conversation.user_id ? 'bg-accent' : ''
                }`}
                onClick={() => onConversationSelect(conversation.user_id, conversation.user_name)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium truncate">{conversation.user_name}</h3>
                      {conversation.unread_count > 0 && (
                        <Badge variant="destructive" className="text-xs">
                          {conversation.unread_count}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground truncate mt-1">
                      {conversation.last_message.message}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(conversation.last_message.created_at).toLocaleString()}
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
