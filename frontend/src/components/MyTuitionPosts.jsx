import React, { useState, useEffect } from 'react'

function MyTuitionPosts({ currentUser, token, API_URL, setCurrentView, openAuthModal }) {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

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

  return (
    <div className="my-posts-container">
      <div className="page-header flex-between">
        <div>
          <h2>📋 My Tuition Posts</h2>
          <p className="subtitle">Manage and track your active tuition job postings.</p>
        </div>
        {(currentUser.role === 'Guardian' || currentUser.role === 'Student') && (
          <button className="btn btn-primary" onClick={() => setCurrentView('post-tuition')}>
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
          {(currentUser.role === 'Guardian' || currentUser.role === 'Student') ? (
            <button className="btn btn-primary mt-3" onClick={() => setCurrentView('post-tuition')}>
              Post Your First Tuition Job
            </button>
          ) : (
            <p className="text-info mt-2">Log in with a Guardian or Student role to post tuitions.</p>
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

              <div className="post-card-footer flex-between">
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
