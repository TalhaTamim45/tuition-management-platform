import React, { useState, useEffect } from 'react'

function MyApplications({ currentUser, token, API_URL, setCurrentView, openAuthModal }) {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!currentUser || !token) {
      setLoading(false)
      return
    }

    fetchMyApplications()
  }, [currentUser, token])

  const fetchMyApplications = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/api/applications/my-applications`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()

      if (response.ok && data.success) {
        setApplications(data.applications || [])
      } else {
        setError(data.error || 'Failed to fetch your applications.')
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
        <h2>📩 My Applications</h2>
        <p className="lead">Please log in to track your tuition job applications.</p>
        <div className="mt-4">
          <button className="btn btn-primary btn-lg" onClick={openAuthModal}>
            Sign In / Register
          </button>
        </div>
      </div>
    )
  }

  const isTutor = currentUser.role?.toLowerCase() === 'tutor'

  if (!isTutor) {
    return (
      <div className="card text-center p-5 auth-guard-card">
        <h2>🚫 Access Restricted</h2>
        <p className="lead">Only accounts registered as <strong>Tutors</strong> can apply for tuition jobs and view this page.</p>
        <p className="text-muted">If you are a Client, you can manage applications submitted to your posts from "My Tuition Posts".</p>
      </div>
    )
  }

  return (
    <div className="my-applications-container">
      <div className="page-header flex-between">
        <div>
          <h2>📩 My Job Applications</h2>
          <p className="subtitle">Track statuses of tuition posts you have applied to.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setCurrentView('home')}>
          🔍 Browse More Jobs
        </button>
      </div>

      {error && <div className="alert alert-danger">⚠️ {error}</div>}

      {loading ? (
        <div className="text-center p-5">
          <div className="spinner large-spinner"></div>
          <p className="mt-3">Loading your applications...</p>
        </div>
      ) : applications.length === 0 ? (
        <div className="empty-state card text-center p-5">
          <div className="empty-icon">📤</div>
          <h3>No Applications Yet</h3>
          <p className="text-muted">You have not applied to any tuition jobs yet.</p>
          <button className="btn btn-primary mt-3" onClick={() => setCurrentView('home')}>
            Explore Available Tuition Jobs
          </button>
        </div>
      ) : (
        <div className="posts-grid">
          {applications.map(app => {
            const post = app.tuition_post
            if (!post) return null
            return (
              <div key={app.id} className="post-card card">
                <div className="post-card-header flex-between">
                  <h3 className="post-title">{post.title}</h3>
                  <span className={`status-badge status-${app.status.toLowerCase()}`}>
                    {app.status.toUpperCase()}
                  </span>
                </div>

                <div className="post-details-grid">
                  <div className="detail-item">
                    <span className="detail-label">🎓 Student Class:</span>
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
                </div>

                <div className="post-card-footer flex-between" style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border)', paddingTop: '0.75rem' }}>
                  <span className="created-date" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    📤 Applied on: {app.applied_at ? new Date(app.applied_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'}
                  </span>
                  <span className="post-id" style={{ fontSize: '0.8rem' }}>Job Status: <strong>{post.status.toUpperCase()}</strong></span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default MyApplications
