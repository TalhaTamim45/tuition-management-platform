import React from 'react'

function Navbar({ currentView, setCurrentView, currentUser, onLogout, openAuthModal }) {
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
      </div>

      <div className="nav-auth">
        {currentUser ? (
          <div className="user-profile-badge">
            <div className="user-info">
              <span className="user-name">{currentUser.name}</span>
              <span className={`user-role-badge role-${currentUser.role?.toLowerCase()}`}>
                {currentUser.role}
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
