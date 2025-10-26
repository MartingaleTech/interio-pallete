import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Download, AlertCircle } from 'lucide-react'
import { fileService, FileMetadata } from '../../../../services/fileService'

interface FilePreviewProps {
  fileId: string
  token: string
  isOpen: boolean
  onClose: () => void
}

export function FilePreview({ fileId, token, isOpen, onClose }: FilePreviewProps) {
  const [metadata, setMetadata] = useState<FileMetadata | null>(null)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen && fileId) {
      fetchFileData()
    }
  }, [isOpen, fileId])

  const fetchFileData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [metadataRes, downloadRes] = await Promise.all([
        fileService.getFileMetadata(token, fileId),
        fileService.getDownloadUrl(token, fileId)
      ])
      setMetadata(metadataRes)
      setDownloadUrl(downloadRes.download_url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load file')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (downloadUrl) {
      window.open(downloadUrl, '_blank')
    }
  }

  const renderPreview = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64 sm:h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading preview...</p>
          </div>
        </div>
      )
    }

    if (error || !metadata || !downloadUrl) {
      return (
        <div className="flex items-center justify-center h-64 sm:h-96">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-500">{error || 'Failed to load file'}</p>
          </div>
        </div>
      )
    }

    if (metadata.file_type.startsWith('image/')) {
      return (
        <div className="flex items-center justify-center bg-gray-100 rounded-lg p-4 max-h-[70vh] overflow-auto">
          <img
            src={metadata.thumbnail_url || downloadUrl}
            alt={metadata.file_name}
            className="max-w-full max-h-full object-contain rounded"
            onError={(e) => {
              if (metadata.thumbnail_url && e.currentTarget.src !== downloadUrl) {
                e.currentTarget.src = downloadUrl
              }
            }}
          />
        </div>
      )
    }

    if (metadata.file_type === 'application/pdf') {
      return (
        <div className="h-[70vh] w-full">
          <iframe
            src={downloadUrl}
            className="w-full h-full rounded-lg border"
            title={metadata.file_name}
          />
        </div>
      )
    }

    if (
      metadata.file_type.includes('model/') ||
      metadata.file_name.match(/\.(obj|fbx|skp|stl|gltf|glb)$/i)
    ) {
      return (
        <div className="flex items-center justify-center h-64 sm:h-96 bg-gray-100 rounded-lg">
          <div className="text-center p-6">
            <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <p className="text-lg font-medium mb-2">3D Model File</p>
            <p className="text-sm text-gray-500 mb-4">
              {metadata.file_name}
            </p>
            <p className="text-xs text-gray-400 mb-4">
              3D preview coming soon. Download to view in your 3D software.
            </p>
            <Button onClick={handleDownload} size="sm">
              <Download className="w-4 h-4 mr-2" />
              Download to View
            </Button>
          </div>
        </div>
      )
    }

    return (
      <div className="flex items-center justify-center h-64 sm:h-96 bg-gray-100 rounded-lg">
        <div className="text-center p-6">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium mb-2">Preview Not Available</p>
          <p className="text-sm text-gray-500 mb-4">
            This file type cannot be previewed in the browser
          </p>
          <Button onClick={handleDownload} size="sm">
            <Download className="w-4 h-4 mr-2" />
            Download File
          </Button>
        </div>
      </div>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0 pr-4">
              <DialogTitle className="text-lg sm:text-xl truncate">
                {metadata?.file_name || 'File Preview'}
              </DialogTitle>
              {metadata && (
                <div className="mt-2 space-y-1 text-sm text-gray-500">
                  <p>Version {metadata.version}</p>
                  <p>Uploaded by {metadata.uploaded_by_name}</p>
                  <p>{new Date(metadata.created_at).toLocaleString()}</p>
                  <p>Size: {formatFileSize(metadata.file_size)}</p>
                  <p>Downloads: {metadata.download_count}</p>
                </div>
              )}
            </div>
            <div className="flex gap-2">
              {downloadUrl && (
                <Button onClick={handleDownload} size="sm" variant="outline">
                  <Download className="w-4 h-4 sm:mr-2" />
                  <span className="hidden sm:inline">Download</span>
                </Button>
              )}
            </div>
          </div>
        </DialogHeader>
        <div className="mt-4">
          {renderPreview()}
        </div>
      </DialogContent>
    </Dialog>
  )
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
