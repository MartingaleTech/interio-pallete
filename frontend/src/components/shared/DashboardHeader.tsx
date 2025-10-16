import { Building2, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface DashboardHeaderProps {
  title: string
  userName: string
  onLogout: () => void
}

export function DashboardHeader({ title, userName, onLogout }: DashboardHeaderProps) {
  return (
    <header className="bg-white border-b sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
            <Building2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Interio Palette</h1>
            <p className="text-sm text-gray-500">{title}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium">{userName}</span>
          <Button onClick={onLogout} variant="outline" size="sm">
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </header>
  )
}
