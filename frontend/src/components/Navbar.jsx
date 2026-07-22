import React from 'react'

function Navbar({ currentView, setCurrentView, currentUser, onLogout, openAuthModal }) {
  const userRole = currentUser?.role?.toLowerCase() || ''

  return (
    <nav className="navbar">
      <div className="nav-brand" onClick={() => setCurrentView('home')}>
        <span className="logo-icon">🎓</span>
        <span className="logo-text">Tuition Management Platform</span>
      </div>

      <div className="nav-links">
        <button
          className={`nav-btn ${currentView === 'home' ? 'active' : ''}`}
          onClick={() => setCurrentView('home')}
        >
          Home
        </button>

        {/* Client Links */}
        {userRole === 'client' && (
          <>
            <button
              className={`nav-btn ${currentView === 'post-tuition' ? 'active' : ''}`}
              onClick={() => setCurrentView('post-tuition')}
            >
              ➕ Post Tuition
            </button>
            <button
              className={`nav-btn ${currentView === 'my-posts' ? 'active' : ''}`}
              onClick={() => setCurrentView('my-posts')}
            >
              📋 My Tuition Posts
            </button>
          </>
        )}

        {/* Public or Unauthenticated User can see Post Tuition button which opens auth guard */}
        {!currentUser && (
          <button
            className={`nav-btn ${currentView === 'post-tuition' ? 'active' : ''}`}
            onClick={() => setCurrentView('post-tuition')}
          >
            ➕ Post Tuition
          </button>
        )}

        {/* Admin Links */}
        {userRole === 'admin' && (
          <>
            <button
              className={`nav-btn ${currentView === 'admin-dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('admin-dashboard')}
            >
              📊 Admin Dashboard
            </button>
            <button
              className={`nav-btn ${currentView === 'admin-users' ? 'active' : ''}`}
              onClick={() => setCurrentView('admin-users')}
            >
              👥 Manage Users
            </button>
            <button
              className={`nav-btn ${currentView === 'admin-posts' ? 'active' : ''}`}
              onClick={() => setCurrentView('admin-posts')}
            >
              📑 Manage Posts
            </button>
          </>
        )}
      </div>

      <div className="nav-auth">
        {currentUser ? (
          <div className="user-profile-badge">
            <div className="user-info">
              <span className="user-name">{currentUser.name}</span>
              <span className={`user-role-badge role-${userRole}`}>
                {userRole.toUpperCase()}
              </span>
            </div>
            <button className="btn btn-outline-danger btn-sm" onClick={onLogout}>
              Logout
            </button>
          </div>
        ) : (
          <button className="btn btn-primary" onClick={openAuthModal}>
            Sign In / Register
          </button>
        )}
      </div>
    </nav>
  )
}

export default Navbar
