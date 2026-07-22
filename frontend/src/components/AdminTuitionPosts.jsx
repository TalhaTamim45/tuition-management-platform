import React, { useState, useEffect } from 'react'

function AdminTuitionPosts({ currentUser, token, API_URL, openAuthModal }) {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const [deleteModal, setDeleteModal] = useState({
    isOpen: false,
    post: null
  })

  useEffect(() => {
    if (!currentUser || currentUser.role?.toLowerCase() !== 'admin') {
      setLoading(false)
      return
    }

    fetchPosts()
  }, [currentUser, token])

  const fetchPosts = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/api/admin/tuition-posts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()

      if (response.ok && data.success) {
        setPosts(data.posts || [])
      } else {
        setError(data.error || 'Failed to fetch admin tuition posts.')
      }
    } catch (err) {
      setError('Network error connecting to backend API.')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleStatus = async (post) => {
    const newStatus = post.status === 'open' ? 'closed' : 'open'
    setError('')
    setSuccessMsg('')

    try {
      const response = await fetch(`${API_URL}/api/admin/tuition-posts/${post.id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      })

      const data = await response.json()
      if (response.ok && data.success) {
        setSuccessMsg(data.message)
        fetchPosts()
      } else {
        setError(data.error || 'Failed to update post status.')
      }
    } catch (err) {
      setError('Network error updating post status.')
    }
  }

  const executeDeletePost = async () => {
    const post = deleteModal.post
    if (!post) return

    setDeleteModal({ isOpen: false, post: null })
    setError('')
    setSuccessMsg('')

    try {
      const response = await fetch(`${API_URL}/api/admin/tuition-posts/${post.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      const data = await response.json()
      if (response.ok && data.success) {
        setSuccessMsg(data.message)
        fetchPosts()
      } else {
        setError(data.error || 'Failed to delete post.')
      }
    } catch (err) {
      setError('Network error deleting post.')
    }
  }

  if (!currentUser || currentUser.role?.toLowerCase() !== 'admin') {
    return (
      <div className="card text-center p-5 auth-guard-card">
        <h2>🚫 Admin Access Restricted</h2>
        <p className="lead">You must be logged in as an <strong>Admin</strong> to manage tuition job posts.</p>
        <div className="mt-4">
          <button className="btn btn-primary" onClick={openAuthModal}>
            Sign In as Admin
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-posts-container">
      <div className="page-header flex-between mb-4">
        <div>
          <h2>📑 Admin Tuition Post Management</h2>
          <p className="subtitle">Moderate, close, reopen, or remove inappropriate tuition job postings.</p>
        </div>
        <button className="btn btn-outline" onClick={fetchPosts}>
          🔄 Refresh Posts
        </button>
      </div>

      {successMsg && <div className="alert alert-success">{successMsg}</div>}
      {error && <div className="alert alert-danger">⚠️ {error}</div>}

      {loading ? (
        <div className="text-center p-5">
          <div className="spinner large-spinner"></div>
          <p className="mt-3">Loading tuition job postings...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="card text-center p-5">
          <h3>No Tuition Posts Found</h3>
          <p className="text-muted">There are no tuition posts in the database.</p>
        </div>
      ) : (
        <div className="table-responsive card">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Client Name</th>
                <th>Class</th>
                <th>Subjects</th>
                <th>Location</th>
                <th>Salary</th>
                <th>Status</th>
                <th>Posted Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {posts.map(p => (
                <tr key={p.id}>
                  <td>#{p.id}</td>
                  <td><strong>{p.title}</strong></td>
                  <td>{p.client_name || 'Client'}</td>
                  <td>{p.student_class}</td>
                  <td>{p.subjects}</td>
                  <td>{p.location} ({p.teaching_mode})</td>
                  <td>৳{Number(p.monthly_salary).toLocaleString()}</td>
                  <td>
                    <span className={`status-badge status-${p.status}`}>
                      {p.status.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    {p.created_at ? new Date(p.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'}
                  </td>
                  <td>
                    <div className="action-buttons-group">
                      <button
                        className="btn btn-sm btn-outline"
                        onClick={() => handleToggleStatus(p)}
                      >
                        {p.status === 'open' ? '🔴 Close' : '🟢 Reopen'}
                      </button>
                      <button
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => setDeleteModal({ isOpen: true, post: p })}
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteModal.isOpen && (
        <div className="modal-backdrop">
          <div className="modal-card modal-sm">
            <h3>🗑️ Confirm Post Deletion</h3>
            <p className="mt-3">
              Are you sure you want to permanently delete tuition post{' '}
              <strong>#{deleteModal.post?.id}: "{deleteModal.post?.title}"</strong>?
            </p>
            <p className="text-danger mt-2 font-sm">
              This action cannot be undone.
            </p>
            <div className="modal-actions mt-4 flex-between">
              <button
                className="btn btn-outline"
                onClick={() => setDeleteModal({ isOpen: false, post: null })}
              >
                Cancel
              </button>
              <button
                className="btn btn-outline-danger"
                onClick={executeDeletePost}
              >
                Yes, Delete Post
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminTuitionPosts
