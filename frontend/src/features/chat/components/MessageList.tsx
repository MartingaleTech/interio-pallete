import { useEffect, useRef } from 'react'
import { useChat } from '../../../state/ChatContext'
import { useAuth } from '../../../state/AuthContext'
import { ChatMessage } from '../../../types/chat'
import { ScrollArea } from '../../../components/ui/scroll-area'
import { Button } from '../../../components/ui/button'
import { Pencil, Trash2, Check, CheckCheck } from 'lucide-react'

interface MessageListProps {
  onEditMessage?: (message: ChatMessage) => void
}

export function MessageList({ onEditMessage }: MessageListProps) {
  const { currentMessages, typingUsers, deleteMessage } = useChat()
  const { user } = useAuth()
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [currentMessages])

  const handleDelete = (messageId: string, isOwnMessage: boolean) => {
    if (confirm('Are you sure you want to delete this message?')) {
      deleteMessage(messageId, isOwnMessage)
    }
  }

  const getReadStatus = (message: ChatMessage) => {
    if (!message.read_receipts || message.read_receipts.length === 0) {
      return 'sent'
    }

    const hasRead = message.read_receipts.some(r => r.read_at)
    const hasDelivered = message.read_receipts.some(r => r.delivered_at)

    if (hasRead) return 'read'
    if (hasDelivered) return 'delivered'
    return 'sent'
  }

  return (
    <div className="flex-1 flex flex-col">
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {currentMessages.map((message) => {
            const isOwnMessage = message.sender_id === user?.id
            const readStatus = getReadStatus(message)

            return (
              <div
                key={message.id}
                className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    isOwnMessage
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  {!isOwnMessage && (
                    <div className="text-xs font-semibold mb-1">
                      {message.sender_name}
                    </div>
                  )}
                  
                  {message.is_deleted ? (
                    <div className="text-sm italic opacity-70">
                      This message was deleted
                    </div>
                  ) : (
                    <>
                      {message.parent_message_id && (
                        <div className="text-xs opacity-70 mb-2 pb-2 border-b border-current/20">
                          Replying to a message
                        </div>
                      )}
                      
                      <div className="text-sm whitespace-pre-wrap break-words">
                        {message.message}
                      </div>

                      {message.attachment_url && (
                        <div className="mt-2 p-2 bg-background/10 rounded">
                          <a
                            href={message.attachment_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs underline"
                          >
                            {message.attachment_name || 'Attachment'}
                          </a>
                          {message.attachment_size && (
                            <span className="text-xs ml-2">
                              ({(message.attachment_size / 1024).toFixed(1)} KB)
                            </span>
                          )}
                        </div>
                      )}
                    </>
                  )}

                  <div className="flex items-center justify-between mt-2 gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs opacity-70">
                        {new Date(message.created_at).toLocaleTimeString()}
                      </span>
                      {message.is_edited && (
                        <span className="text-xs opacity-70">(edited)</span>
                      )}
                    </div>

                    <div className="flex items-center gap-1">
                      {isOwnMessage && !message.is_deleted && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={() => onEditMessage?.(message)}
                          >
                            <Pencil className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={() => handleDelete(message.id, true)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </>
                      )}
                      
                      {isOwnMessage && (
                        <div className="ml-1">
                          {readStatus === 'read' && (
                            <CheckCheck className="h-3 w-3" />
                          )}
                          {readStatus === 'delivered' && (
                            <CheckCheck className="h-3 w-3 opacity-50" />
                          )}
                          {readStatus === 'sent' && (
                            <Check className="h-3 w-3 opacity-50" />
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}

          {typingUsers.length > 0 && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg p-3 text-sm">
                <span className="font-semibold">
                  {typingUsers.map(t => t.user_name).join(', ')}
                </span>
                <span className="ml-1">
                  {typingUsers.length === 1 ? 'is' : 'are'} typing...
                </span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
