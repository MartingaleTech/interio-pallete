import { useState, useRef, useEffect } from 'react'
import { useChat } from '../../../state/ChatContext'
import { ChatMessage } from '../../../types/chat'
import { Button } from '../../../components/ui/button'
import { Textarea } from '../../../components/ui/textarea'
import { Send, X } from 'lucide-react'

interface MessageInputProps {
  roomId?: string
  recipientId?: string
  editingMessage?: ChatMessage | null
  onCancelEdit?: () => void
}

export function MessageInput({ roomId, recipientId, editingMessage, onCancelEdit }: MessageInputProps) {
  const { sendMessage, sendDirectMessage, editMessage, startTyping, stopTyping } = useChat()
  const [message, setMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (editingMessage) {
      setMessage(editingMessage.message)
      textareaRef.current?.focus()
    }
  }, [editingMessage])

  const handleTyping = (value: string) => {
    setMessage(value)

    if (value.trim() && !isTyping) {
      setIsTyping(true)
      startTyping(roomId, recipientId)
    }

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    typingTimeoutRef.current = setTimeout(() => {
      if (isTyping) {
        setIsTyping(false)
        stopTyping(roomId, recipientId)
      }
    }, 3000)
  }

  const handleSend = () => {
    const trimmedMessage = message.trim()
    if (!trimmedMessage) return

    if (editingMessage) {
      editMessage(editingMessage.id, trimmedMessage)
      onCancelEdit?.()
    } else if (roomId) {
      sendMessage(roomId, trimmedMessage)
    } else if (recipientId) {
      sendDirectMessage(recipientId, trimmedMessage)
    }

    setMessage('')
    
    if (isTyping) {
      setIsTyping(false)
      stopTyping(roomId, recipientId)
    }

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleCancel = () => {
    setMessage('')
    onCancelEdit?.()
    
    if (isTyping) {
      setIsTyping(false)
      stopTyping(roomId, recipientId)
    }
  }

  return (
    <div className="border-t p-4">
      {editingMessage && (
        <div className="mb-2 flex items-center justify-between bg-muted p-2 rounded">
          <span className="text-sm">Editing message</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCancel}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}
      
      <div className="flex gap-2">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => handleTyping(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          className="min-h-[60px] max-h-[200px] resize-none"
        />
        <Button
          onClick={handleSend}
          disabled={!message.trim()}
          size="icon"
          className="h-[60px] w-[60px]"
        >
          <Send className="h-5 w-5" />
        </Button>
      </div>
      
      <div className="text-xs text-muted-foreground mt-2">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  )
}
