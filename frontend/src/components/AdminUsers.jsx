import React, { useState, useEffect } from 'react'

function AdminUsers({ currentUser, token, API_URL, openAuthModal }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  const [confirmModal, setConfirmModal] = useState({
    isOpen: false,
    user: null,
    action: ''
  })

  useEffect(() => {
    if (!currentUser || currentUser.role?.toLowerCase() !== 'admin') {
      setLoading(false)
      return
    }

    fetchUsers()
  }, [currentUser, token, search, roleFilter, statusFilter])

  const fetchUsers = async () => {
    setLoading(true)
    setError('')
    try {
      const queryParams = new URLSearchParams()
      if (search) queryParams.append('search', search)
      if (roleFilter !== 'all') queryParams.append('role', roleFilter)
      if (statusFilter !== 'all') queryParams.append('status', statusFilter)

      const response = await fetch(`${API_URL}/api/admin/users?${queryParams.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()

      if (response.ok && data.success) {
        setUsers(data.users || [])
      } else {
        setError(data.error || 'Failed to fetch users.')
      }
    } catch (err) {
      setError('Network error connecting to backend API.')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusToggleRequest = (user) => {
    if (user.id === currentUser.id) {
      alert("⚠️ You cannot block your own admin account.")
      return
    }
    const action = user.is_blocked ? 'unblock' : 'block'
    setConfirmModal({
      isOpen: true,
      user,
      action
    })
  }

  const executeStatusToggle = async () => {
    const { user, action } = confirmModal
    if (!user) return

    setConfirmModal({ isOpen: false, user: null, action: '' })
    setError('')
    setSuccessMsg('')

    try {
      const response = await fetch(`${API_URL}/api/admin/users/${user.id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_blocked: action === 'block' })
      })

      const data = await response.json()
      if (response.ok && data.success) {
        setSuccessMsg(data.message)
        fetchUsers()
      } else {
        setError(data.error || 'Failed to update user status.')
      }
    } catch (err) {
      setError('Network error updating user status.')
    }
  }

  if (!currentUser || currentUser.role?.toLowerCase() !== 'admin') {
    return (
      <div className="card text-center p-5 auth-guard-card">
        <h2>🚫 Admin Access Restricted</h2>
        <p className="lead">You must be logged in as an <strong>Admin</strong> to manage platform users.</p>
        <div className="mt-4">
          <button className="btn btn-primary" onClick={openAuthModal}>
            Sign In as Admin
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-users-container">
      <div className="page-header flex-between mb-4">
        <div>
          <h2>👥 Admin User Management</h2>
          <p className="subtitle">View, filter, search, and manage account statuses across the platform.</p>
        </div>
        <button className="btn btn-outline" onClick={fetchUsers}>
          🔄 Refresh Users List
        </button>
      </div>

      {successMsg && <div className="alert alert-success">{successMsg}</div>}
      {error && <div className="alert alert-danger">⚠️ {error}</div>}

      {/* Search & Filter Toolbar */}
      <div className="filter-toolbar card mb-4">
        <div className="form-row grid-3">
          <div className="form-group">
            <label>🔍 Search by Name or Email</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Type name or email..."
            />
          </div>

          <div className="form-group">
            <label>🎭 Filter by Role</label>
            <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
              <option value="all">All Roles</option>
              <option value="client">Client</option>
              <option value="tutor">Tutor</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div className="form-group">
            <label>⚡ Filter by Status</label>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      {loading ? (
        <div className="text-center p-5">
          <div className="spinner large-spinner"></div>
          <p className="mt-3">Loading user directory...</p>
        </div>
      ) : users.length === 0 ? (
        <div className="card text-center p-5">
          <h3>No Users Found</h3>
          <p className="text-muted">No user records matched your current search and filter criteria.</p>
        </div>
      ) : (
        <div className="table-responsive card">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Registered Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className={u.is_blocked ? 'row-blocked' : ''}>
                  <td>#{u.id}</td>
                  <td>
                    <strong>{u.name}</strong>
                    {u.id === currentUser.id && <span className="badge-you">(You)</span>}
                  </td>
                  <td>{u.email}</td>
                  <td>
                    <span className={`role-badge role-${u.role}`}>
                      {u.role.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge status-${u.is_blocked ? 'blocked' : 'active'}`}>
                      {u.is_blocked ? '⛔ BLOCKED' : '✅ ACTIVE'}
                    </span>
                  </td>
                  <td>
                    {u.created_at ? new Date(u.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'}
                  </td>
                  <td>
                    {u.id === currentUser.id ? (
                      <span className="text-muted font-sm">N/A (Self)</span>
                    ) : (
                      <button
                        className={`btn btn-sm ${u.is_blocked ? 'btn-success' : 'btn-outline-danger'}`}
                        onClick={() => handleStatusToggleRequest(u)}
                      >
                        {u.is_blocked ? '🔓 Unblock' : '⛔ Block'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Confirmation Modal */}
      {confirmModal.isOpen && (
        <div className="modal-backdrop">
          <div className="modal-card modal-sm">
            <h3>⚠️ Confirm Account {confirmModal.action === 'block' ? 'Block' : 'Unblock'}</h3>
            <p className="mt-3">
              Are you sure you want to <strong>{confirmModal.action}</strong> user{' '}
              <strong>{confirmModal.user?.name}</strong> ({confirmModal.user?.email})?
            </p>
            {confirmModal.action === 'block' && (
              <p className="text-danger mt-2 font-sm">
                Blocked users will be immediately denied access to sign in or use any platform services.
              </p>
            )}
            <div className="modal-actions mt-4 flex-between">
              <button
                className="btn btn-outline"
                onClick={() => setConfirmModal({ isOpen: false, user: null, action: '' })}
              >
                Cancel
              </button>
              <button
                className={`btn ${confirmModal.action === 'block' ? 'btn-outline-danger' : 'btn-primary'}`}
                onClick={executeStatusToggle}
              >
                Yes, {confirmModal.action.toUpperCase()}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminUsers
