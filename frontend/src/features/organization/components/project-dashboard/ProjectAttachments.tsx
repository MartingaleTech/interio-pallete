import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { 
  Plus, FileText, Image as ImageIcon, Download, Trash2, 
  MessageSquare, History, Shield, Eye, MoreVertical 
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Project } from '../../../../types'
import { fileService, FileMetadata } from '../../../../services/fileService'
import { FileUpload } from '../file-management/FileUpload'
import { FilePreview } from '../file-management/FilePreview'
import { FileComments } from '../file-management/FileComments'
import { VersionHistory } from '../file-management/VersionHistory'
import { FilePermissions } from '../file-management/FilePermissions'
import { useAuth } from '../../../../state/AuthContext'
import { projectService } from '../../../../services/projectService'

interface ProjectAttachmentsProps {
  project: Project
  token: string
}

export function ProjectAttachments({ project, token }: ProjectAttachmentsProps) {
  const { user } = useAuth()
  const [files, setFiles] = useState<FileMetadata[]>([])
  const [loading, setLoading] = useState(true)
  const [showUploadDialog, setShowUploadDialog] = useState(false)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [showComments, setShowComments] = useState(false)
  const [showVersions, setShowVersions] = useState(false)
  const [showPermissions, setShowPermissions] = useState(false)
  const [teamMembers, setTeamMembers] = useState<any[]>([])

  useEffect(() => {
    fetchFiles()
    fetchTeamMembers()
  }, [project.id])

  const fetchFiles = async () => {
    setLoading(true)
    try {
      const data = await fileService.listFiles(token, project.id)
      setFiles(data)
    } catch (error) {
      console.error('Failed to fetch files', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTeamMembers = async () => {
    try {
      const data = await projectService.getProjectTeam(token, project.id)
      setTeamMembers(data)
    } catch (error) {
      console.error('Failed to fetch team members', error)
    }
  }

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
      return
    }

    try {
      await fileService.deleteFile(token, fileId)
      alert('File deleted successfully!')
      fetchFiles()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to delete file')
    }
  }

  const handleDownload = async (fileId: string) => {
    try {
      const downloadData = await fileService.getDownloadUrl(token, fileId)
      window.open(downloadData.download_url, '_blank')
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to download file')
    }
  }

  const openFileActions = (fileId: string, action: 'preview' | 'comments' | 'versions' | 'permissions') => {
    setSelectedFile(fileId)
    switch (action) {
      case 'preview':
        setShowPreview(true)
        break
      case 'comments':
        setShowComments(true)
        break
      case 'versions':
        setShowVersions(true)
        break
      case 'permissions':
        setShowPermissions(true)
        break
    }
  }

  const closeAllDialogs = () => {
    setShowPreview(false)
    setShowComments(false)
    setShowVersions(false)
    setShowPermissions(false)
    setSelectedFile(null)
  }

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) {
      return <ImageIcon className="w-5 h-5 text-blue-500" />
    }
    return <FileText className="w-5 h-5 text-gray-500" />
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const getFileTypeLabel = (fileName: string): string => {
    const ext = fileName.split('.').pop()?.toUpperCase()
    return ext || 'FILE'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold mb-2">Attachments & Designs</h2>
          <p className="text-gray-600">
            All design files and attachments for this project ({files.length} files)
          </p>
        </div>
        <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
          <DialogTrigger asChild>
            <Button className="w-full sm:w-auto">
              <Plus className="w-4 h-4 mr-2" />
              Upload Files
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Upload Files</DialogTitle>
            </DialogHeader>
            <FileUpload
              projectId={project.id}
              token={token}
              onUploadComplete={() => {
                setShowUploadDialog(false)
                fetchFiles()
              }}
              onCancel={() => setShowUploadDialog(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Files Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading files...</p>
        </div>
      ) : files.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium mb-2">No files yet</p>
            <p className="text-sm mb-4">Upload your first design file or attachment to get started</p>
            <Button onClick={() => setShowUploadDialog(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Upload Files
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {files.map((file) => (
            <Card key={file.id} className="hover:shadow-lg transition-shadow group">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    {getFileIcon(file.file_type)}
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-base truncate">{file.file_name}</CardTitle>
                      <p className="text-xs text-gray-500 mt-1">
                        v{file.version} • {getFileTypeLabel(file.file_name)}
                      </p>
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => openFileActions(file.id, 'preview')}>
                        <Eye className="w-4 h-4 mr-2" />
                        Preview
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleDownload(file.id)}>
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => openFileActions(file.id, 'comments')}>
                        <MessageSquare className="w-4 h-4 mr-2" />
                        Comments
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => openFileActions(file.id, 'versions')}>
                        <History className="w-4 h-4 mr-2" />
                        Version History
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => openFileActions(file.id, 'permissions')}>
                        <Shield className="w-4 h-4 mr-2" />
                        Permissions
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={() => handleDelete(file.id)}
                        className="text-red-600"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                {/* Thumbnail Preview */}
                {file.thumbnail_url && (
                  <div 
                    className="mb-3 rounded-lg overflow-hidden bg-gray-100 cursor-pointer"
                    onClick={() => openFileActions(file.id, 'preview')}
                  >
                    <img
                      src={file.thumbnail_url}
                      alt={file.file_name}
                      className="w-full h-32 object-cover hover:scale-105 transition-transform"
                    />
                  </div>
                )}

                {/* File Info */}
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{formatFileSize(file.file_size)}</span>
                    <span>{file.download_count} downloads</span>
                  </div>
                  <div className="pt-2 border-t">
                    <p className="text-xs text-gray-500">
                      Uploaded by {file.uploaded_by_name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(file.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="mt-3 grid grid-cols-2 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openFileActions(file.id, 'preview')}
                    className="w-full"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    Preview
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openFileActions(file.id, 'comments')}
                    className="w-full"
                  >
                    <MessageSquare className="w-4 h-4 mr-1" />
                    Comments
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* File Preview Dialog */}
      {selectedFile && (
        <FilePreview
          fileId={selectedFile}
          token={token}
          isOpen={showPreview}
          onClose={closeAllDialogs}
        />
      )}

      {/* File Comments Dialog */}
      {selectedFile && (
        <Dialog open={showComments} onOpenChange={(open) => !open && closeAllDialogs()}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>File Comments</DialogTitle>
            </DialogHeader>
            <FileComments
              fileId={selectedFile}
              token={token}
              currentUserId={user?.id || ''}
              currentUserName={user?.name || ''}
              teamMembers={teamMembers}
            />
          </DialogContent>
        </Dialog>
      )}

      {/* Version History Dialog */}
      {selectedFile && (
        <VersionHistory
          fileId={selectedFile}
          token={token}
          isOpen={showVersions}
          onClose={closeAllDialogs}
          onVersionRestored={fetchFiles}
        />
      )}

      {/* File Permissions Dialog */}
      {selectedFile && (
        <FilePermissions
          fileId={selectedFile}
          token={token}
          isOpen={showPermissions}
          onClose={closeAllDialogs}
          teamMembers={teamMembers}
        />
      )}
    </div>
  )
}
