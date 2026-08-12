import React, { useState, useEffect } from 'react'

function MyTuitionPosts({ currentUser, token, API_URL, setCurrentView, openAuthModal, handleEditPost, clearEditPostId }) {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [expandedPosts, setExpandedPosts] = useState({}) // maps postId -> boolean
  const [postApps, setPostApps] = useState({}) // maps postId -> array of applications
  const [loadingApps, setLoadingApps] = useState({}) // maps postId -> boolean

  useEffect(() => {
    if (!currentUser || !token) {
      setLoading(false)
      return
    }

    fetchMyPosts()
  }, [currentUser, token])

  const fetchMyPosts = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/api/tuition-posts/my-posts`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()

      if (response.ok && data.success) {
        setPosts(data.posts || [])
      } else {
        setError(data.error || 'Failed to fetch your tuition posts.')
      }
    } catch (err) {
      setError('Network error connecting to backend API.')
    } finally {
      setLoading(false)
    }
  }

  const handleDeletePost = async (postId) => {
    if (!window.confirm("Are you sure you want to delete this tuition post? This action cannot be undone.")) {
      return
    }
    try {
      const response = await fetch(`${API_URL}/api/tuition-posts/${postId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (response.ok && data.success) {
        alert("Tuition post deleted successfully.")
        setPosts(prev => prev.filter(p => p.id !== postId))
      } else {
        alert(data.error || "Failed to delete tuition post.")
      }
    } catch (err) {
      alert("Network error deleting tuition post.")
    }
  }

  const toggleApplications = async (postId) => {
    const isExpanded = !expandedPosts[postId]
    setExpandedPosts(prev => ({ ...prev, [postId]: isExpanded }))

    if (isExpanded) {
      setLoadingApps(prev => ({ ...prev, [postId]: true }))
      try {
        const response = await fetch(`${API_URL}/api/tuition-posts/${postId}/applications`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        const data = await response.json()
        if (response.ok && data.success) {
          setPostApps(prev => ({ ...prev, [postId]: data.applications || [] }))
        } else {
          console.error(data.error || "Failed to load applications")
        }
      } catch (err) {
        console.error("Network error fetching applications", err)
      } finally {
        setLoadingApps(prev => ({ ...prev, [postId]: false }))
      }
    }
  }

  const handleApproveReject = async (postId, applicationId, newStatus) => {
    try {
      const response = await fetch(`${API_URL}/api/applications/${applicationId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      })
      const data = await response.json()
      if (response.ok && data.success) {
        alert(`Application successfully ${newStatus}.`)
        setPostApps(prev => ({
          ...prev,
          [postId]: prev[postId].map(app => 
            app.id === applicationId ? { ...app, status: newStatus } : app
          )
        }))
      } else {
        alert(data.error || `Failed to update application status.`)
      }
    } catch (err) {
      alert("Network error updating application status.")
    }
  }

  if (!currentUser) {
    return (
      <div className="card text-center p-5 auth-guard-card">
        <h2>📋 My Tuition Posts</h2>
        <p className="lead">Please log in to view your posted tuition requirements.</p>
        <div className="mt-4">
          <button className="btn btn-primary btn-lg" onClick={openAuthModal}>
            Sign In / Register
          </button>
        </div>
      </div>
    )
  }

  const isClient = currentUser.role?.toLowerCase() === 'client'

  return (
    <div className="my-posts-container">
      <div className="page-header flex-between">
        <div>
          <h2>📋 My Tuition Posts</h2>
          <p className="subtitle">Manage and track your active tuition job postings.</p>
        </div>
        {isClient && (
          <button className="btn btn-primary" onClick={() => {
            if (typeof clearEditPostId === 'function') clearEditPostId()
            setCurrentView('post-tuition')
          }}>
            ➕ Post New Tuition
          </button>
        )}
      </div>

      {error && <div className="alert alert-danger">⚠️ {error}</div>}

      {loading ? (
        <div className="text-center p-5">
          <div className="spinner large-spinner"></div>
          <p className="mt-3">Loading your tuition posts...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="empty-state card text-center p-5">
          <div className="empty-icon">📭</div>
          <h3>No Tuition Posts Found</h3>
          <p className="text-muted">You have not created any tuition job postings yet.</p>
          {isClient ? (
            <button className="btn btn-primary mt-3" onClick={() => {
              if (typeof clearEditPostId === 'function') clearEditPostId()
              setCurrentView('post-tuition')
            }}>
              Post Your First Tuition Job
            </button>
          ) : (
            <p className="text-info mt-2">Log in with a Client account to post tuitions.</p>
          )}
        </div>
      ) : (
        <div className="posts-grid">
          {posts.map(post => (
            <div key={post.id} className="post-card card">
              <div className="post-card-header flex-between">
                <h3 className="post-title">{post.title}</h3>
                <span className={`status-badge status-${post.status.toLowerCase()}`}>
                  {post.status.toUpperCase()}
                </span>
              </div>

              <div className="post-details-grid">
                <div className="detail-item">
                  <span className="detail-label">🎓 Class:</span>
                  <span className="detail-value">{post.student_class}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">📖 Subjects:</span>
                  <span className="detail-value">{post.subjects}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">📍 Location:</span>
                  <span className="detail-value">{post.location}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">💰 Monthly Salary:</span>
                  <span className="detail-value highlight-salary">
                    ৳{Number(post.monthly_salary).toLocaleString()} BDT
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">💻 Teaching Mode:</span>
                  <span className={`badge-mode mode-${post.teaching_mode.toLowerCase()}`}>
                    {post.teaching_mode}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">📅 Days / Week:</span>
                  <span className="detail-value">{post.days_per_week} days/week</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">👤 Preferred Tutor:</span>
                  <span className="detail-value">{post.preferred_tutor_gender || 'Any'}</span>
                </div>
              </div>

              {post.additional_notes && (
                <div className="post-notes">
                  <strong>Notes:</strong> {post.additional_notes}
                </div>
              )}

              <div className="card-actions flex-between" style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                <div className="action-buttons-group">
                  <button 
                    className="btn btn-secondary btn-sm" 
                    onClick={() => handleEditPost(post.id)}
                  >
                    ✏️ Edit
                  </button>
                  <button 
                    className="btn btn-outline-danger btn-sm" 
                    onClick={() => handleDeletePost(post.id)}
                  >
                    🗑️ Delete
                  </button>
                </div>
                
                <button 
                  className="btn btn-outline btn-sm" 
                  onClick={() => toggleApplications(post.id)}
                >
                  📩 {expandedPosts[post.id] ? 'Hide Applications' : 'View Applications'}
                </button>
              </div>

              {/* Collapsible Applications Section */}
              {expandedPosts[post.id] && (
                <div className="applications-section" style={{ marginTop: '1rem', background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <h4 style={{ marginBottom: '0.75rem', fontSize: '0.95rem', color: 'var(--primary)' }}>👤 Tutor Applications</h4>
                  {loadingApps[post.id] ? (
                    <div className="text-center p-3">
                      <span className="spinner large-spinner" style={{ width: '20px', height: '20px' }}></span> Loading...
                    </div>
                  ) : !postApps[post.id] || postApps[post.id].length === 0 ? (
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>No tutors have applied for this post yet.</p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {postApps[post.id].map(app => (
                        <div key={app.id} style={{ background: '#ffffff', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border)', fontSize: '0.85rem' }}>
                          <div className="flex-between" style={{ marginBottom: '0.5rem' }}>
                            <strong>{app.tutor_name}</strong>
                            <span className={`status-badge status-${app.status}`}>
                              {app.status.toUpperCase()}
                            </span>
                          </div>
                          
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem 1rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                            <p>📞 <strong>Phone:</strong> {app.tutor_phone || 'N/A'}</p>
                            <p>📧 <strong>Email:</strong> {app.tutor_email}</p>
                            <p>🎓 <strong>Education:</strong> {app.tutor_education || 'N/A'} ({app.tutor_institution || 'N/A'})</p>
                            <p>📖 <strong>Subjects:</strong> {app.tutor_subjects || 'N/A'}</p>
                            <p>💼 <strong>Experience:</strong> {app.tutor_experience || 'N/A'}</p>
                            <p>💰 <strong>Expectation:</strong> ৳{Number(app.tutor_salary_expectation).toLocaleString()} BDT</p>
                          </div>
                          
                          {app.status === 'pending' && (
                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                              <button 
                                className="btn btn-success btn-sm" 
                                style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                                onClick={() => handleApproveReject(post.id, app.id, 'accepted')}
                              >
                                ✅ Accept Tutor
                              </button>
                              <button 
                                className="btn btn-outline-danger btn-sm" 
                                style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                                onClick={() => handleApproveReject(post.id, app.id, 'rejected')}
                              >
                                ❌ Reject Tutor
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className="post-card-footer flex-between" style={{ marginTop: '1rem' }}>
                <span className="created-date">
                  📅 Posted on: {post.created_at ? new Date(post.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'}
                </span>
                <span className="post-id">Job ID #{post.id}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MyTuitionPosts
