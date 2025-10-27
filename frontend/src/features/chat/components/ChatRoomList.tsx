import { useEffect } from 'react'
import { useChat } from '../../../state/ChatContext'
import { ChatRoom } from '../../../types/chat'
import { Card } from '../../../components/ui/card'
import { Badge } from '../../../components/ui/badge'
import { ScrollArea } from '../../../components/ui/scroll-area'

interface ChatRoomListProps {
  onRoomSelect: (room: ChatRoom) => void
}

export function ChatRoomList({ onRoomSelect }: ChatRoomListProps) {
  const { rooms, currentRoom, loadRooms } = useChat()

  useEffect(() => {
    loadRooms()
  }, [loadRooms])

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Chat Rooms</h2>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-2">
          {rooms.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No chat rooms available
            </div>
          ) : (
            rooms.map((room) => (
              <Card
                key={room.id}
                className={`p-3 cursor-pointer hover:bg-accent transition-colors ${
                  currentRoom?.id === room.id ? 'bg-accent' : ''
                }`}
                onClick={() => onRoomSelect(room)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium truncate">{room.name}</h3>
                      {room.unread_count && room.unread_count > 0 && (
                        <Badge variant="destructive" className="text-xs">
                          {room.unread_count}
                        </Badge>
                      )}
                    </div>
                    {room.description && (
                      <p className="text-sm text-muted-foreground truncate mt-1">
                        {room.description}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(room.updated_at).toLocaleString()}
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
