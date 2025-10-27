import { useState } from 'react'
import { useChat } from '../../../state/ChatContext'
import { ChatRoom, ChatMessage } from '../../../types/chat'
import { ChatRoomList } from './ChatRoomList'
import { DirectMessages } from './DirectMessages'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs'
import { Card } from '../../../components/ui/card'

export function Chat() {
  const { currentRoom, setCurrentRoom, currentDirectUserId, setCurrentDirectUserId, isConnected } = useChat()
  const [editingMessage, setEditingMessage] = useState<ChatMessage | null>(null)
  const [currentDirectUserName, setCurrentDirectUserName] = useState<string | null>(null)

  const handleRoomSelect = (room: ChatRoom) => {
    setCurrentRoom(room)
    setCurrentDirectUserId(null)
    setCurrentDirectUserName(null)
    setEditingMessage(null)
  }

  const handleConversationSelect = (userId: string, userName: string) => {
    setCurrentDirectUserId(userId)
    setCurrentDirectUserName(userName)
    setCurrentRoom(null)
    setEditingMessage(null)
  }

  const handleEditMessage = (message: ChatMessage) => {
    setEditingMessage(message)
  }

  const handleCancelEdit = () => {
    setEditingMessage(null)
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Chat</h1>
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-muted-foreground">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-80 border-r">
          <Tabs defaultValue="rooms" className="h-full flex flex-col">
            <TabsList className="w-full">
              <TabsTrigger value="rooms" className="flex-1">Rooms</TabsTrigger>
              <TabsTrigger value="direct" className="flex-1">Direct</TabsTrigger>
            </TabsList>
            <TabsContent value="rooms" className="flex-1 overflow-hidden m-0">
              <ChatRoomList onRoomSelect={handleRoomSelect} />
            </TabsContent>
            <TabsContent value="direct" className="flex-1 overflow-hidden m-0">
              <DirectMessages onConversationSelect={handleConversationSelect} />
            </TabsContent>
          </Tabs>
        </div>

        <div className="flex-1 flex flex-col">
          {currentRoom || currentDirectUserId ? (
            <>
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold">
                  {currentRoom ? currentRoom.name : currentDirectUserName}
                </h2>
                {currentRoom?.description && (
                  <p className="text-sm text-muted-foreground">{currentRoom.description}</p>
                )}
              </div>
              <MessageList onEditMessage={handleEditMessage} />
              <MessageInput
                roomId={currentRoom?.id}
                recipientId={currentDirectUserId || undefined}
                editingMessage={editingMessage}
                onCancelEdit={handleCancelEdit}
              />
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <Card className="p-8 text-center">
                <h3 className="text-lg font-semibold mb-2">No conversation selected</h3>
                <p className="text-muted-foreground">
                  Select a chat room or direct message to start chatting
                </p>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
