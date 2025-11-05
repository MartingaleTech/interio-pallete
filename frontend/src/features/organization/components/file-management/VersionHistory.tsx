import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { History, RotateCcw, Download, Upload, Check } from 'lucide-react'
import { fileService, FileVersion } from '../../../../services/fileService'

interface VersionHistoryProps {
  fileId: string
  token: string
  isOpen: boolean
  onClose: () => void
  onVersionRestored: () => void
}

export function VersionHistory({ fileId, token, isOpen, onClose, onVersionRestored }: VersionHistoryProps) {
  const [versions, setVersions] = useState<FileVersion[]>([])
  const [loading, setLoading] = useState(true)
  const [restoring, setRestoring] = useState<string | null>(null)
  const [uploadingNew, setUploadingNew] = useState(false)

  useEffect(() => {
    if (isOpen && fileId) {
      fetchVersions()
    }
  }, [isOpen, fileId])

  const fetchVersions = async () => {
    setLoading(true)
    try {
      const data = await fileService.getVersionHistory(token, fileId)
      setVersions(data)
    } catch (error) {
      console.error('Failed to fetch version history', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRestore = async (versionId: string) => {
    if (!confirm('Are you sure you want to restore this version? This will create a new version based on the selected one.')) {
      return
    }

    setRestoring(versionId)
    try {
      await fileService.restoreVersion(token, versionId)
      alert('Version restored successfully!')
      fetchVersions()
      onVersionRestored()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to restore version')
    } finally {
      setRestoring(null)
    }
  }

  const handleUploadNewVersion = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploadingNew(true)
    try {
      await fileService.uploadNewVersion(token, fileId, file)
      alert('New version uploaded successfully!')
      fetchVersions()
      onVersionRestored()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to upload new version')
    } finally {
      setUploadingNew(false)
      event.target.value = '' // Reset file input
    }
  }

  const handleDownload = async (versionId: string) => {
    try {
      const downloadData = await fileService.getDownloadUrl(token, versionId)
      window.open(downloadData.download_url, '_blank')
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to download version')
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center gap-2 text-lg sm:text-xl">
              <History className="w-5 h-5" />
              Version History
            </DialogTitle>
            <div className="relative">
              <input
                type="file"
                id="new-version-upload"
                className="hidden"
                onChange={handleUploadNewVersion}
                disabled={uploadingNew}
              />
              <Button
                size="sm"
                onClick={() => document.getElementById('new-version-upload')?.click()}
                disabled={uploadingNew}
              >
                <Upload className="w-4 h-4 mr-2" />
                {uploadingNew ? 'Uploading...' : 'Upload New Version'}
              </Button>
            </div>
          </div>
        </DialogHeader>

        <div className="mt-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-500 mt-2">Loading version history...</p>
            </div>
          ) : versions.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-gray-500">
                No version history available
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {/* Timeline */}
              <div className="relative">
                {versions.map((version, index) => (
                  <div key={version.id} className="relative pb-6">
                    {/* Timeline Line */}
                    {index < versions.length - 1 && (
                      <div className="absolute left-4 top-8 bottom-0 w-0.5 bg-gray-200" />
                    )}

                    {/* Version Card */}
                    <div className="flex gap-4">
                      {/* Timeline Dot */}
                      <div className="relative flex-shrink-0">
                        <div
                          className={`
                            w-8 h-8 rounded-full flex items-center justify-center
                            ${version.is_latest_version
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-200 text-gray-600'
                            }
                          `}
                        >
                          {version.is_latest_version ? (
                            <Check className="w-4 h-4" />
                          ) : (
                            <span className="text-xs font-medium">v{version.version}</span>
                          )}
                        </div>
                      </div>

                      {/* Version Details */}
                      <Card className={`flex-1 ${version.is_latest_version ? 'border-blue-500 border-2' : ''}`}>
                        <CardContent className="p-3 sm:p-4">
                          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap mb-2">
                                <h4 className="font-semibold text-sm sm:text-base">
                                  Version {version.version}
                                </h4>
                                {version.is_latest_version && (
                                  <span className="inline-flex items-center px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                                    Current
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-gray-600 truncate mb-1">
                                {version.file_name}
                              </p>
                              <div className="text-xs text-gray-500 space-y-0.5">
                                <p>Uploaded by {version.uploaded_by_name}</p>
                                <p>{new Date(version.created_at).toLocaleString()}</p>
                              </div>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2 flex-wrap sm:flex-nowrap">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDownload(version.id)}
                                className="flex-1 sm:flex-none"
                              >
                                <Download className="w-4 h-4 sm:mr-2" />
                                <span className="hidden sm:inline">Download</span>
                              </Button>
                              {!version.is_latest_version && (
                                <Button
                                  size="sm"
                                  onClick={() => handleRestore(version.id)}
                                  disabled={restoring === version.id}
                                  className="flex-1 sm:flex-none"
                                >
                                  <RotateCcw className="w-4 h-4 sm:mr-2" />
                                  <span className="hidden sm:inline">
                                    {restoring === version.id ? 'Restoring...' : 'Restore'}
                                  </span>
                                </Button>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                ))}
              </div>

              {/* Info Box */}
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-3 sm:p-4">
                  <p className="text-sm text-blue-800">
                    <strong>Note:</strong> Restoring a previous version will create a new version based on the selected one. 
                    The current version will be preserved in the history.
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
