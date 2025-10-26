import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Plus, Paperclip, FileText, Image } from 'lucide-react'
import { Project } from '../../../../types'
import { projectService } from '../../../../services/projectService'

interface ProjectAttachmentsProps {
  project: Project
  token: string
}

export function ProjectAttachments({ project, token }: ProjectAttachmentsProps) {
  const [designs, setDesigns] = useState<any[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    file_url: '',
    file_type: ''
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchDesigns()
  }, [])

  const fetchDesigns = async () => {
    try {
      const data = await projectService.getProjectDesigns(token, project.id)
      setDesigns(data)
    } catch (error) {
      console.error('Failed to fetch designs', error)
    }
  }

  const handleSubmit = async () => {
    if (!formData.title || !formData.description || !formData.file_url || !formData.file_type) {
      alert('Please fill all fields')
      return
    }

    setLoading(true)
    try {
      await projectService.createProjectDesign(token, project.id, formData)
      alert('Design/Attachment added successfully!')
      setShowDialog(false)
      setFormData({ title: '', description: '', file_url: '', file_type: '' })
      fetchDesigns()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to add design')
    } finally {
      setLoading(false)
    }
  }

  const getFileIcon = (fileType: string) => {
    if (fileType.includes('image')) return <Image className="w-5 h-5" />
    return <FileText className="w-5 h-5" />
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold mb-2">Attachments & Designs</h2>
          <p className="text-gray-600">All design files and attachments for this project</p>
        </div>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Attachment
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Add Design/Attachment</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  placeholder="Design title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Design description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="file_url">File URL</Label>
                <Input
                  id="file_url"
                  placeholder="https://example.com/file.pdf"
                  value={formData.file_url}
                  onChange={(e) => setFormData({ ...formData, file_url: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="file_type">File Type</Label>
                <Input
                  id="file_type"
                  placeholder="e.g., image/png, application/pdf"
                  value={formData.file_type}
                  onChange={(e) => setFormData({ ...formData, file_type: e.target.value })}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} className="flex-1" disabled={loading}>
                {loading ? 'Adding...' : 'Add Attachment'}
              </Button>
              <Button onClick={() => setShowDialog(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {designs.map((design) => (
          <Card key={design.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                {getFileIcon(design.file_type)}
                {design.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm text-gray-700">{design.description}</p>
                <div className="pt-2 border-t">
                  <p className="text-xs text-gray-500">Uploaded by {design.uploaded_by}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(design.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full mt-2"
                  onClick={() => window.open(design.file_url, '_blank')}
                >
                  <Paperclip className="w-4 h-4 mr-2" />
                  View File
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {designs.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No attachments or designs yet. Add files to this project.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
