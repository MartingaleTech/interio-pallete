import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Shield, Plus, Eye, Download, MessageSquare, Trash } from 'lucide-react'
import { fileService, FilePermission } from '../../../../services/fileService'

interface FilePermissionsProps {
  fileId: string
  token: string
  isOpen: boolean
  onClose: () => void
  teamMembers?: Array<{ id: string; name: string; role: string }>
}

const PERMISSION_TYPES = [
  { value: 'view', label: 'View', icon: Eye, description: 'Can view file metadata and preview' },
  { value: 'download', label: 'Download', icon: Download, description: 'Can download the file' },
  { value: 'comment', label: 'Comment', icon: MessageSquare, description: 'Can add comments' },
  { value: 'delete', label: 'Delete', icon: Trash, description: 'Can delete the file' }
]

export function FilePermissions({ fileId, token, isOpen, onClose, teamMembers = [] }: FilePermissionsProps) {
  const [permissions, setPermissions] = useState<FilePermission[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedUser, setSelectedUser] = useState<string>('')
  const [selectedPermission, setSelectedPermission] = useState<string>('view')
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    if (isOpen && fileId) {
      fetchPermissions()
    }
  }, [isOpen, fileId])

  const fetchPermissions = async () => {
    setLoading(true)
    try {
      const data = await fileService.getPermissions(token, fileId)
      setPermissions(data)
    } catch (error) {
      console.error('Failed to fetch permissions', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddPermission = async () => {
    if (!selectedUser) {
      alert('Please select a user')
      return
    }

    setAdding(true)
    try {
      await fileService.setPermission(token, fileId, selectedUser, selectedPermission)
      alert('Permission added successfully!')
      setSelectedUser('')
      setSelectedPermission('view')
      fetchPermissions()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to add permission')
    } finally {
      setAdding(false)
    }
  }

  const getUserName = (userId: string): string => {
    const user = teamMembers.find(m => m.id === userId)
    return user ? user.name : 'Unknown User'
  }

  const getPermissionIcon = (permissionType: string) => {
    const permission = PERMISSION_TYPES.find(p => p.value === permissionType)
    if (!permission) return null
    const Icon = permission.icon
    return <Icon className="w-4 h-4" />
  }

  const getPermissionLabel = (permissionType: string): string => {
    const permission = PERMISSION_TYPES.find(p => p.value === permissionType)
    return permission ? permission.label : permissionType
  }

  const availableUsers = teamMembers.filter(
    member => !permissions.some(p => p.user_id === member.id && p.permission_type === selectedPermission)
  )

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-lg sm:text-xl">
            <Shield className="w-5 h-5" />
            File Permissions
          </DialogTitle>
        </DialogHeader>

        <div className="mt-4 space-y-6">
          {/* Add Permission Form */}
          <Card>
            <CardContent className="p-4">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Plus className="w-4 h-4" />
                Add Permission
              </h3>
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">User</label>
                    <Select value={selectedUser} onValueChange={setSelectedUser}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select user" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableUsers.map((member) => (
                          <SelectItem key={member.id} value={member.id}>
                            {member.name} ({member.role})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Permission Type</label>
                    <Select value={selectedPermission} onValueChange={setSelectedPermission}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {PERMISSION_TYPES.map((perm) => (
                          <SelectItem key={perm.value} value={perm.value}>
                            <div className="flex items-center gap-2">
                              <perm.icon className="w-4 h-4" />
                              {perm.label}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                {selectedPermission && (
                  <p className="text-xs text-gray-500">
                    {PERMISSION_TYPES.find(p => p.value === selectedPermission)?.description}
                  </p>
                )}
                <Button
                  onClick={handleAddPermission}
                  disabled={adding || !selectedUser}
                  className="w-full sm:w-auto"
                >
                  {adding ? 'Adding...' : 'Add Permission'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Current Permissions */}
          <div className="space-y-3">
            <h3 className="font-semibold">Current Permissions</h3>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-gray-500 mt-2">Loading permissions...</p>
              </div>
            ) : permissions.length === 0 ? (
              <Card>
                <CardContent className="py-8 text-center text-gray-500">
                  No specific permissions set. File uses default project permissions.
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {/* Group permissions by user */}
                {Array.from(new Set(permissions.map(p => p.user_id || p.role))).map((identifier) => {
                  const userPermissions = permissions.filter(
                    p => (p.user_id || p.role) === identifier
                  )
                  const isRole = !userPermissions[0].user_id
                  const displayName = isRole
                    ? `Role: ${userPermissions[0].role}`
                    : getUserName(identifier!)

                  return (
                    <Card key={identifier}>
                      <CardContent className="p-3 sm:p-4">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm sm:text-base truncate">
                              {displayName}
                            </p>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {userPermissions.map((perm) => (
                                <span
                                  key={perm.id}
                                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                                >
                                  {getPermissionIcon(perm.permission_type)}
                                  {getPermissionLabel(perm.permission_type)}
                                </span>
                              ))}
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              Added {new Date(userPermissions[0].created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            )}
          </div>

          {/* Permission Types Reference */}
          <Card className="bg-gray-50">
            <CardContent className="p-4">
              <h4 className="font-semibold mb-3 text-sm">Permission Types</h4>
              <div className="space-y-2">
                {PERMISSION_TYPES.map((perm) => (
                  <div key={perm.value} className="flex items-start gap-2 text-sm">
                    <perm.icon className="w-4 h-4 mt-0.5 text-gray-600" />
                    <div>
                      <span className="font-medium">{perm.label}:</span>{' '}
                      <span className="text-gray-600">{perm.description}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  )
}
