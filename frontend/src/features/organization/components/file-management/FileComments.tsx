import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { MessageSquare, Send, Edit2, Trash2, Check, X, ChevronDown, ChevronRight } from 'lucide-react'
import { fileService, FileComment } from '../../../../services/fileService'

interface FileCommentsProps {
  fileId: string
  token: string
  currentUserId: string
  currentUserName: string
  teamMembers?: Array<{ id: string; name: string }>
}

interface CommentItemProps {
  comment: FileComment
  token: string
  currentUserId: string
  onReply: (parentId: string) => void
  onUpdate: () => void
  onDelete: (commentId: string) => void
  onResolve: (commentId: string, isResolved: boolean) => void
  level?: number
}

function CommentItem({ comment, token, currentUserId, onReply, onUpdate, onDelete, onResolve, level = 0 }: CommentItemProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [isEditing, setIsEditing] = useState(false)
  const [editText, setEditText] = useState(comment.comment)
  const [updating, setUpdating] = useState(false)

  const isOwner = comment.user_id === currentUserId
  const hasReplies = comment.replies && comment.replies.length > 0
  const indentClass = level > 0 ? `ml-${Math.min(level * 4, 12)}` : ''

  const handleUpdate = async () => {
    if (!editText.trim()) return
    
    setUpdating(true)
    try {
      await fileService.updateComment(token, comment.id, editText)
      setIsEditing(false)
      onUpdate()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to update comment')
    } finally {
      setUpdating(false)
    }
  }

  const handleResolveToggle = async () => {
    try {
      await onResolve(comment.id, !comment.is_resolved)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to update comment status')
    }
  }

  const renderCommentText = (text: string) => {
    const parts = text.split(/(@\w+)/g)
    return parts.map((part, index) => {
      if (part.startsWith('@')) {
        return (
          <span key={index} className="text-blue-600 font-medium">
            {part}
          </span>
        )
      }
      return <span key={index}>{part}</span>
    })
  }

  return (
    <div className={`${indentClass} ${level > 0 ? 'border-l-2 border-gray-200 pl-4' : ''}`}>
      <Card className={`mb-3 ${comment.is_resolved ? 'bg-green-50 border-green-200' : ''}`}>
        <CardContent className="p-3 sm:p-4">
          {/* Comment Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-sm">{comment.user_name}</span>
                <span className="text-xs text-gray-500">
                  {new Date(comment.created_at).toLocaleString()}
                </span>
                {comment.is_resolved && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                    <Check className="w-3 h-3" />
                    Resolved
                  </span>
                )}
              </div>
              {comment.resolved_by && (
                <p className="text-xs text-gray-500 mt-1">
                  Resolved by {comment.resolved_by} on {new Date(comment.resolved_at!).toLocaleString()}
                </p>
              )}
            </div>
            {hasReplies && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="ml-2"
              >
                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                <span className="ml-1 text-xs">{comment.replies!.length}</span>
              </Button>
            )}
          </div>

          {/* Comment Body */}
          {isEditing ? (
            <div className="space-y-2">
              <Textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="min-h-[80px]"
                disabled={updating}
              />
              <div className="flex gap-2">
                <Button size="sm" onClick={handleUpdate} disabled={updating}>
                  {updating ? 'Saving...' : 'Save'}
                </Button>
                <Button size="sm" variant="outline" onClick={() => setIsEditing(false)} disabled={updating}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-700 mb-3 whitespace-pre-wrap break-words">
              {renderCommentText(comment.comment)}
            </div>
          )}

          {/* Comment Actions */}
          {!isEditing && (
            <div className="flex flex-wrap gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onReply(comment.id)}
                className="text-xs"
              >
                <MessageSquare className="w-3 h-3 mr-1" />
                Reply
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleResolveToggle}
                className="text-xs"
              >
                {comment.is_resolved ? (
                  <>
                    <X className="w-3 h-3 mr-1" />
                    Unresolve
                  </>
                ) : (
                  <>
                    <Check className="w-3 h-3 mr-1" />
                    Resolve
                  </>
                )}
              </Button>
              {isOwner && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                    className="text-xs"
                  >
                    <Edit2 className="w-3 h-3 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(comment.id)}
                    className="text-xs text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-3 h-3 mr-1" />
                    Delete
                  </Button>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Nested Replies */}
      {isExpanded && hasReplies && (
        <div className="space-y-2">
          {comment.replies!.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              token={token}
              currentUserId={currentUserId}
              onReply={onReply}
              onUpdate={onUpdate}
              onDelete={onDelete}
              onResolve={onResolve}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function FileComments({ fileId, token, currentUserId, teamMembers = [] }: FileCommentsProps) {
  const [comments, setComments] = useState<FileComment[]>([])
  const [loading, setLoading] = useState(true)
  const [newComment, setNewComment] = useState('')
  const [replyingTo, setReplyingTo] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [showResolved, setShowResolved] = useState(true)
  const [showMentionSuggestions, setShowMentionSuggestions] = useState(false)
  const [mentionSearch, setMentionSearch] = useState('')

  useEffect(() => {
    fetchComments()
  }, [fileId])

  const fetchComments = async () => {
    setLoading(true)
    try {
      const data = await fileService.getThreadedComments(token, fileId)
      setComments(data)
    } catch (error) {
      console.error('Failed to fetch comments', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCommentChange = (text: string) => {
    setNewComment(text)
    
    const lastAtIndex = text.lastIndexOf('@')
    if (lastAtIndex !== -1 && lastAtIndex === text.length - 1) {
      setShowMentionSuggestions(true)
      setMentionSearch('')
    } else if (lastAtIndex !== -1) {
      const afterAt = text.substring(lastAtIndex + 1)
      if (!afterAt.includes(' ')) {
        setShowMentionSuggestions(true)
        setMentionSearch(afterAt)
      } else {
        setShowMentionSuggestions(false)
      }
    } else {
      setShowMentionSuggestions(false)
    }
  }

  const insertMention = (username: string) => {
    const lastAtIndex = newComment.lastIndexOf('@')
    const beforeAt = newComment.substring(0, lastAtIndex)
    const afterMention = newComment.substring(lastAtIndex + 1 + mentionSearch.length)
    setNewComment(`${beforeAt}@${username} ${afterMention}`)
    setShowMentionSuggestions(false)
  }

  const handleSubmit = async () => {
    if (!newComment.trim()) return

    setSubmitting(true)
    try {
      await fileService.createComment(token, fileId, newComment, replyingTo || undefined)
      setNewComment('')
      setReplyingTo(null)
      fetchComments()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to post comment')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (commentId: string) => {
    if (!confirm('Are you sure you want to delete this comment?')) return

    try {
      await fileService.deleteComment(token, commentId)
      fetchComments()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to delete comment')
    }
  }

  const handleResolve = async (commentId: string, isResolved: boolean) => {
    try {
      await fileService.resolveComment(token, commentId, isResolved)
      fetchComments()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to update comment status')
    }
  }

  const filteredComments = showResolved
    ? comments
    : comments.filter(c => !c.is_resolved)

  const filteredTeamMembers = teamMembers.filter(member =>
    member.name.toLowerCase().includes(mentionSearch.toLowerCase())
  )

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          Comments ({comments.length})
        </h3>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowResolved(!showResolved)}
        >
          {showResolved ? 'Hide Resolved' : 'Show Resolved'}
        </Button>
      </div>

      {/* New Comment Form */}
      <Card>
        <CardContent className="p-3 sm:p-4">
          <div className="space-y-2">
            {replyingTo && (
              <div className="flex items-center justify-between bg-blue-50 p-2 rounded text-sm">
                <span className="text-blue-700">Replying to comment...</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setReplyingTo(null)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            )}
            <div className="relative">
              <Textarea
                placeholder="Add a comment... Use @username to mention team members"
                value={newComment}
                onChange={(e) => handleCommentChange(e.target.value)}
                className="min-h-[80px] resize-none"
                disabled={submitting}
              />
              {showMentionSuggestions && filteredTeamMembers.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-48 overflow-y-auto">
                  {filteredTeamMembers.map((member) => (
                    <button
                      key={member.id}
                      className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
                      onClick={() => insertMention(member.name)}
                    >
                      @{member.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="flex justify-between items-center">
              <p className="text-xs text-gray-500">
                Tip: Use @username to mention team members
              </p>
              <Button
                onClick={handleSubmit}
                disabled={submitting || !newComment.trim()}
                size="sm"
              >
                <Send className="w-4 h-4 mr-2" />
                {submitting ? 'Posting...' : 'Post Comment'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comments List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-500 mt-2">Loading comments...</p>
        </div>
      ) : filteredComments.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-gray-500">
            {showResolved ? 'No comments yet. Be the first to comment!' : 'No unresolved comments'}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filteredComments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              token={token}
              currentUserId={currentUserId}
              onReply={setReplyingTo}
              onUpdate={fetchComments}
              onDelete={handleDelete}
              onResolve={handleResolve}
            />
          ))}
        </div>
      )}
    </div>
  )
}
