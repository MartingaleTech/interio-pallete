import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Plus, MessageSquare, Edit, Trash2 } from 'lucide-react'
import { Project, ProjectDailyUpdate } from '../../../../types'
import { projectService } from '../../../../services/projectService'
import { useAuth } from '../../../../state/AuthContext'

interface ProjectDailyUpdatesProps {
  project: Project
  token: string
}

export function ProjectDailyUpdates({ project, token }: ProjectDailyUpdatesProps) {
  const { user } = useAuth()
  const [updates, setUpdates] = useState<ProjectDailyUpdate[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [editingUpdate, setEditingUpdate] = useState<ProjectDailyUpdate | null>(null)
  const [formData, setFormData] = useState({
    update_text: '',
    attachments: ''
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchUpdates()
  }, [])

  const fetchUpdates = async () => {
    try {
      const data = await projectService.getDailyUpdates(token, project.id)
      setUpdates(data)
    } catch (error) {
      console.error('Failed to fetch daily updates', error)
    }
  }

  const handleSubmit = async () => {
    if (!formData.update_text) {
      alert('Please enter an update')
      return
    }

    setLoading(true)
    try {
      if (editingUpdate) {
        await projectService.updateDailyUpdate(token, project.id, editingUpdate.id, formData)
        alert('Update edited successfully!')
      } else {
        await projectService.createDailyUpdate(token, project.id, formData)
        alert('Update posted successfully!')
      }
      setShowDialog(false)
      setEditingUpdate(null)
      setFormData({ update_text: '', attachments: '' })
      fetchUpdates()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to save update')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (update: ProjectDailyUpdate) => {
    setEditingUpdate(update)
    setFormData({
      update_text: update.update_text,
      attachments: update.attachments || ''
    })
    setShowDialog(true)
  }

  const handleDelete = async (updateId: string) => {
    if (!confirm('Are you sure you want to delete this update?')) return

    try {
      await projectService.deleteDailyUpdate(token, project.id, updateId)
      alert('Update deleted successfully!')
      fetchUpdates()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to delete update')
    }
  }

  const handleDialogClose = (open: boolean) => {
    setShowDialog(open)
    if (!open) {
      setEditingUpdate(null)
      setFormData({ update_text: '', attachments: '' })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold mb-2">Daily Updates</h2>
          <p className="text-gray-600">Share progress updates with the team</p>
        </div>
        <Dialog open={showDialog} onOpenChange={handleDialogClose}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Post Update
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>{editingUpdate ? 'Edit Update' : 'Post Daily Update'}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="update_text">Update</Label>
                <Textarea
                  id="update_text"
                  placeholder="What did you work on today?"
                  value={formData.update_text}
                  onChange={(e) => setFormData({ ...formData, update_text: e.target.value })}
                  rows={5}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="attachments">Attachments (optional)</Label>
                <Textarea
                  id="attachments"
                  placeholder="Links to files or images (comma-separated)"
                  value={formData.attachments}
                  onChange={(e) => setFormData({ ...formData, attachments: e.target.value })}
                  rows={2}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={loading}>
                {loading ? 'Saving...' : editingUpdate ? 'Update' : 'Post'}
              </Button>
              <Button onClick={() => handleDialogClose(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-4">
        {updates.map((update) => (
          <Card key={update.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{update.user_name}</CardTitle>
                    <p className="text-sm text-gray-500">
                      {new Date(update.created_at).toLocaleString()}
                      {update.updated_at !== update.created_at && ' (edited)'}
                    </p>
                  </div>
                </div>
                {user && user.id === update.user_id && (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleEdit(update)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(update.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 whitespace-pre-wrap">{update.update_text}</p>
              {update.attachments && (
                <div className="mt-3 pt-3 border-t">
                  <p className="text-sm text-gray-500 mb-2">Attachments:</p>
                  <div className="flex flex-wrap gap-2">
                    {update.attachments.split(',').map((attachment, idx) => (
                      <a
                        key={idx}
                        href={attachment.trim()}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline"
                      >
                        Attachment {idx + 1}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {updates.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No updates yet. Post the first update to share progress with the team.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
