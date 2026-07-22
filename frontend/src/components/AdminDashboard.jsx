import React, { useState, useEffect } from 'react'

function AdminDashboard({ currentUser, token, API_URL, setCurrentView, openAuthModal }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!currentUser || currentUser.role?.toLowerCase() !== 'admin') {
      setLoading(false)
      return
    }

    fetchDashboardStats()
  }, [currentUser, token])

  const fetchDashboardStats = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/api/admin/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()

      if (response.ok && data.success) {
        setStats(data)
      } else {
        setError(data.error || 'Failed to fetch admin dashboard statistics.')
      }
    } catch (err) {
      setError('Network error connecting to backend admin API.')
    } finally {
      setLoading(false)
    }
  }

  if (!currentUser || currentUser.role?.toLowerCase() !== 'admin') {
    return (
      <div className="card text-center p-5 auth-guard-card">
        <h2>🚫 Admin Access Restricted</h2>
        <p className="lead">You must be logged in as an <strong>Admin</strong> to view the System Dashboard.</p>
        <div className="mt-4">
          <button className="btn btn-primary" onClick={openAuthModal}>
            Sign In as Admin
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-dashboard-container">
      <div className="page-header flex-between mb-4">
        <div>
          <h2>📊 Admin Dashboard</h2>
          <p className="subtitle">Real-time system statistics and platform overview.</p>
        </div>
        <button className="btn btn-outline" onClick={fetchDashboardStats}>
          🔄 Refresh Statistics
        </button>
      </div>

      {error && <div className="alert alert-danger">⚠️ {error}</div>}

      {loading ? (
        <div className="text-center p-5">
          <div className="spinner large-spinner"></div>
          <p className="mt-3">Loading dashboard statistics...</p>
        </div>
      ) : stats ? (
        <>
          <div className="admin-metrics-grid">
            <div className="metric-card card-purple">
              <div className="metric-icon">👥</div>
              <div className="metric-data">
                <span className="metric-value">{stats.total_users}</span>
                <span className="metric-label">Total Users</span>
              </div>
            </div>

            <div className="metric-card card-blue">
              <div className="metric-icon">🙋‍♂️</div>
              <div className="metric-data">
                <span className="metric-value">{stats.total_clients}</span>
                <span className="metric-label">Total Clients</span>
              </div>
            </div>

            <div className="metric-card card-green">
              <div className="metric-icon">📚</div>
              <div className="metric-data">
                <span className="metric-value">{stats.total_tutors}</span>
                <span className="metric-label">Total Tutors</span>
              </div>
            </div>

            <div className="metric-card card-orange">
              <div className="metric-icon">📑</div>
              <div className="metric-data">
                <span className="metric-value">{stats.total_tuition_posts}</span>
                <span className="metric-label">Total Tuition Posts</span>
              </div>
            </div>

            <div className="metric-card card-teal">
              <div className="metric-icon">🟢</div>
              <div className="metric-data">
                <span className="metric-value">{stats.open_tuition_posts}</span>
                <span className="metric-label">Open Posts</span>
              </div>
            </div>

            <div className="metric-card card-red">
              <div className="metric-icon">🔴</div>
              <div className="metric-data">
                <span className="metric-value">{stats.closed_tuition_posts}</span>
                <span className="metric-label">Closed Posts</span>
              </div>
            </div>
          </div>

          <div className="admin-quick-actions card mt-4">
            <h3>⚡ Quick Management Shortcuts</h3>
            <div className="quick-buttons-row mt-3">
              <button className="btn btn-primary" onClick={() => setCurrentView('admin-users')}>
                👥 Manage Users ({stats.total_users})
              </button>
              <button className="btn btn-secondary" onClick={() => setCurrentView('admin-posts')}>
                📑 Manage Posts ({stats.total_tuition_posts})
              </button>
            </div>
          </div>
        </>
      ) : null}
    </div>
  )
}

export default AdminDashboard
