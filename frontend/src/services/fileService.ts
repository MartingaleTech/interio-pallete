const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface FileUploadData {
  project_id: string
  title: string
  description: string
}

export interface FileMetadata {
  id: string
  file_name: string
  file_type: string
  file_size: number
  version: number
  uploaded_by_id: string
  uploaded_by_name: string
  created_at: string
  updated_at: string
  thumbnail_url?: string
  download_count: number
  is_public: boolean
  is_latest_version: boolean
}

export interface FileComment {
  id: string
  file_id: string
  user_id: string
  user_name: string
  comment: string
  parent_comment_id?: string
  mentions?: string[]
  is_resolved: boolean
  resolved_by?: string
  resolved_at?: string
  created_at: string
  updated_at: string
  replies?: FileComment[]
}

export interface FilePermission {
  id: string
  file_id: string
  user_id?: string
  role?: string
  permission_type: 'view' | 'download' | 'comment' | 'delete'
  created_at: string
}

export interface FileVersion {
  id: string
  version: number
  file_name: string
  uploaded_by_name: string
  created_at: string
  is_latest_version: boolean
}

export const fileService = {
  async uploadFile(token: string, file: File, data: FileUploadData) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', data.title)
    formData.append('description', data.description)

    const res = await fetch(`${API_URL}/api/projects/${data.project_id}/files/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    })
    if (!res.ok) throw new Error('Failed to upload file')
    return res.json()
  },

  async listFiles(token: string, projectId: string): Promise<FileMetadata[]> {
    const res = await fetch(`${API_URL}/api/projects/${projectId}/files`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch files')
    const json = await res.json()
    
    const files = Array.isArray(json?.files) ? json.files : []
    
    return files.map((file: any) => ({
      ...file,
      uploaded_by_name: file.uploaded_by || file.uploaded_by_name || 'Unknown',
      created_at: file.uploaded_at || file.created_at
    }))
  },

  async getFileMetadata(token: string, fileId: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch file metadata')
    return res.json()
  },

  async getDownloadUrl(token: string, fileId: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}/download`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to get download URL')
    return res.json()
  },

  async deleteFile(token: string, fileId: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to delete file')
    return res.json()
  },

  async createComment(token: string, fileId: string, comment: string, parentCommentId?: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        comment,
        parent_comment_id: parentCommentId
      })
    })
    if (!res.ok) throw new Error('Failed to create comment')
    return res.json()
  },

  async getComments(token: string, fileId: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}/comments`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch comments')
    return res.json()
  },

  async getThreadedComments(token: string, fileId: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}/comments/threaded`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch threaded comments')
    return res.json()
  },

  async updateComment(token: string, commentId: string, comment: string) {
    const res = await fetch(`${API_URL}/api/comments/${commentId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ comment })
    })
    if (!res.ok) throw new Error('Failed to update comment')
    return res.json()
  },

  async deleteComment(token: string, commentId: string) {
    const res = await fetch(`${API_URL}/api/comments/${commentId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to delete comment')
    return res.json()
  },

  async resolveComment(token: string, commentId: string, isResolved: boolean) {
    const res = await fetch(`${API_URL}/api/comments/${commentId}/resolve`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ is_resolved: isResolved })
    })
    if (!res.ok) throw new Error('Failed to resolve comment')
    return res.json()
  },

  async uploadNewVersion(token: string, fileId: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_URL}/api/files/${fileId}/versions/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    })
    if (!res.ok) throw new Error('Failed to upload new version')
    return res.json()
  },

  async getVersionHistory(token: string, fileId: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}/versions`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch version history')
    return res.json()
  },

  async restoreVersion(token: string, versionId: string) {
    const res = await fetch(`${API_URL}/api/files/versions/${versionId}/restore`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to restore version')
    return res.json()
  },

  async setPermission(token: string, fileId: string, userId: string, permissionType: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}/permissions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userId,
        permission_type: permissionType
      })
    })
    if (!res.ok) throw new Error('Failed to set permission')
    return res.json()
  },

  async getPermissions(token: string, fileId: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}/permissions`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch permissions')
    return res.json()
  },

  async getAuditLogs(token: string, fileId: string) {
    const res = await fetch(`${API_URL}/api/files/${fileId}/audit-logs`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch audit logs')
    return res.json()
  }
}
