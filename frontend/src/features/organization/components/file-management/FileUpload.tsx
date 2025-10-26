import { useState, useRef, DragEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Upload, X, FileIcon, Image as ImageIcon, FileText } from 'lucide-react'
import { fileService, FileUploadData } from '../../../../services/fileService'

interface FileUploadProps {
  projectId: string
  token: string
  onUploadComplete: () => void
  onCancel: () => void
}

const ALLOWED_FILE_TYPES = {
  images: ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp'],
  documents: ['application/pdf'],
  models: [
    'model/obj',
    'model/fbx',
    'application/octet-stream', // .obj, .fbx, .skp files
    'model/gltf+json',
    'model/gltf-binary',
    'application/x-sketchup' // .skp
  ]
}

const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB

export function FileUpload({ projectId, token, onUploadComplete, onCancel }: FileUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({})
  const [formData, setFormData] = useState({
    title: '',
    description: ''
  })
  const fileInputRef = useRef<HTMLInputElement>(null)

  const isValidFileType = (file: File): boolean => {
    const allAllowedTypes = [
      ...ALLOWED_FILE_TYPES.images,
      ...ALLOWED_FILE_TYPES.documents,
      ...ALLOWED_FILE_TYPES.models
    ]
    
    if (allAllowedTypes.includes(file.type)) {
      return true
    }
    
    const extension = file.name.split('.').pop()?.toLowerCase()
    const modelExtensions = ['obj', 'fbx', 'skp', 'stl', 'gltf', 'glb']
    return modelExtensions.includes(extension || '')
  }

  const isValidFileSize = (file: File): boolean => {
    return file.size <= MAX_FILE_SIZE
  }

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    addFiles(files)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      addFiles(files)
    }
  }

  const addFiles = (files: File[]) => {
    const validFiles = files.filter(file => {
      if (!isValidFileType(file)) {
        alert(`${file.name}: Invalid file type. Allowed: JPEG, PNG, PDF, OBJ, FBX, SKP, STL, GLTF, GLB`)
        return false
      }
      if (!isValidFileSize(file)) {
        alert(`${file.name}: File too large. Maximum size: 100MB`)
        return false
      }
      return true
    })

    setSelectedFiles(prev => [...prev, ...validFiles])
  }

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <ImageIcon className="w-5 h-5 text-blue-500" />
    }
    if (file.type === 'application/pdf') {
      return <FileText className="w-5 h-5 text-red-500" />
    }
    return <FileIcon className="w-5 h-5 text-gray-500" />
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      alert('Please select at least one file')
      return
    }

    if (!formData.title.trim()) {
      alert('Please enter a title')
      return
    }

    setUploading(true)

    try {
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i]
        const uploadData: FileUploadData = {
          project_id: projectId,
          title: selectedFiles.length > 1 ? `${formData.title} (${i + 1})` : formData.title,
          description: formData.description
        }

        setUploadProgress(prev => ({ ...prev, [file.name]: 0 }))
        
        await fileService.uploadFile(token, file, uploadData)
        
        setUploadProgress(prev => ({ ...prev, [file.name]: 100 }))
      }

      alert('Files uploaded successfully!')
      setSelectedFiles([])
      setFormData({ title: '', description: '' })
      setUploadProgress({})
      onUploadComplete()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to upload files')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Form Fields */}
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="title">Title *</Label>
          <Input
            id="title"
            placeholder="Enter file title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            disabled={uploading}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            placeholder="Enter file description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            disabled={uploading}
            rows={3}
          />
        </div>
      </div>

      {/* Drag and Drop Area */}
      <div
        className={`
          border-2 border-dashed rounded-lg p-6 sm:p-8 text-center transition-colors
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.pdf,.obj,.fbx,.skp,.stl,.gltf,.glb"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />
        <Upload className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-base sm:text-lg font-medium mb-2">
          {isDragging ? 'Drop files here' : 'Drag and drop files here'}
        </p>
        <p className="text-sm text-gray-500 mb-4">or click to browse</p>
        <p className="text-xs text-gray-400">
          Supported: JPEG, PNG, PDF, OBJ, FBX, SKP, STL, GLTF, GLB (Max 100MB)
        </p>
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <Label>Selected Files ({selectedFiles.length})</Label>
          <div className="max-h-48 overflow-y-auto space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {getFileIcon(file)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                    {uploadProgress[file.name] !== undefined && (
                      <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                        <div
                          className="bg-blue-500 h-1.5 rounded-full transition-all"
                          style={{ width: `${uploadProgress[file.name]}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
                {!uploading && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                    className="ml-2"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-2">
        <Button
          onClick={handleUpload}
          disabled={uploading || selectedFiles.length === 0}
          className="flex-1"
        >
          {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} File${selectedFiles.length !== 1 ? 's' : ''}`}
        </Button>
        <Button
          onClick={onCancel}
          variant="outline"
          disabled={uploading}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </div>
  )
}
