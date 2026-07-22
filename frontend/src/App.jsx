import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import PostTuition from './components/PostTuition'
import MyTuitionPosts from './components/MyTuitionPosts'
import AdminDashboard from './components/AdminDashboard'
import AdminUsers from './components/AdminUsers'
import AdminTuitionPosts from './components/AdminTuitionPosts'
import AuthModal from './components/AuthModal'

const API_URL = 'http://localhost:5000'

function App() {
  const [currentView, setCurrentView] = useState('home')
  const [currentUser, setCurrentUser] = useState(null)
  const [token, setToken] = useState('')
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [allPosts, setAllPosts] = useState([])
  const [loadingPosts, setLoadingPosts] = useState(false)

  // Load auth state from localStorage on initial render
  useEffect(() => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (savedToken && savedUser) {
      setToken(savedToken)
      try {
        setCurrentUser(JSON.parse(savedUser))
      } catch (e) {
        localStorage.removeItem('user')
      }
    }

    fetchAllPosts()
  }, [])

  const fetchAllPosts = async () => {
    setLoadingPosts(true)
    try {
      const res = await fetch(`${API_URL}/api/tuition-posts`)
      const data = await res.json()
      if (res.ok && data.success) {
        setAllPosts(data.posts || [])
      }
    } catch (e) {
      console.error('Failed to fetch public tuition posts:', e)
    } finally {
      setLoadingPosts(false)
    }
  }

  const handleLoginSuccess = (user, token) => {
    setCurrentUser(user)
    setToken(token)
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('token', token)

    // Redirect admin user directly to admin dashboard
    if (user.role?.toLowerCase() === 'admin') {
      setCurrentView('admin-dashboard')
    }
  }

  const handleLogout = () => {
    setCurrentUser(null)
    setToken('')
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    setCurrentView('home')
  }

  return (
    <div className="app-container">
      <Navbar
        currentView={currentView}
        setCurrentView={setCurrentView}
        currentUser={currentUser}
        onLogout={handleLogout}
        openAuthModal={() => setIsAuthModalOpen(true)}
      />

      <main className="main-content">
        {currentView === 'home' && (
          <div className="home-view">
            <header className="hero-section text-center">
              <h1>Tuition Management Platform</h1>
              <p className="subtitle">Connect directly with qualified tutors & home tuition jobs in Bangladesh</p>
              <div className="hero-actions">
                <button
                  className="btn btn-primary btn-lg"
                  onClick={() => {
                    if (currentUser?.role?.toLowerCase() === 'client' || !currentUser) {
                      setCurrentView('post-tuition')
                    } else if (currentUser?.role?.toLowerCase() === 'admin') {
                      setCurrentView('admin-dashboard')
                    } else {
                      alert('Only Client accounts can post tuitions. Log in as a Client.')
                    }
                  }}
                >
                  ➕ Post a Tuition Requirement
                </button>
                {currentUser?.role?.toLowerCase() === 'admin' ? (
                  <button
                    className="btn btn-secondary btn-lg"
                    onClick={() => setCurrentView('admin-dashboard')}
                  >
                    📊 Open Admin Dashboard
                  </button>
                ) : (
                  <button
                    className="btn btn-secondary btn-lg"
                    onClick={() => setCurrentView('my-posts')}
                  >
                    📋 View My Posts
                  </button>
                )}
              </div>
            </header>

            <section className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">🙋‍♂️</div>
                <h3>For Clients (Parents & Students)</h3>
                <p>Post tuition requirements with customized salary, subjects, and preferred tutor gender. Connect directly with qualified tutors.</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">📚</div>
                <h3>For Tutors</h3>
                <p>Browse verified home and online tuition jobs, apply without middleman commissions, and build a trusted teaching profile.</p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">⚙️</div>
                <h3>For Administrators</h3>
                <p>Comprehensive admin dashboard, user management, account moderation/blocking, and job post content management.</p>
              </div>
            </section>

            {/* Public Tuition Job Feed */}
            <section className="recent-posts-section">
              <div className="section-header flex-between">
                <h2>📢 Available Tuition Jobs ({allPosts.length})</h2>
                <button className="btn btn-outline" onClick={fetchAllPosts}>
                  🔄 Refresh Feed
                </button>
              </div>

              {loadingPosts ? (
                <div className="text-center p-4"><div className="spinner"></div></div>
              ) : allPosts.length === 0 ? (
                <div className="card text-center p-4">
                  <p>No tuition posts currently available. Be the first to post!</p>
                </div>
              ) : (
                <div className="posts-grid">
                  {allPosts.map(post => (
                    <div key={post.id} className="post-card card">
                      <div className="post-card-header flex-between">
                        <h3>{post.title}</h3>
                        <span className={`status-badge status-${post.status}`}>{post.status.toUpperCase()}</span>
                      </div>
                      <div className="post-details">
                        <p>🎓 <strong>Class:</strong> {post.student_class} | 📖 <strong>Subjects:</strong> {post.subjects}</p>
                        <p>📍 <strong>Location:</strong> {post.location} ({post.teaching_mode})</p>
                        <p>💰 <strong>Salary:</strong> ৳{Number(post.monthly_salary).toLocaleString()} BDT/month ({post.days_per_week} days/wk)</p>
                      </div>
                      {post.additional_notes && <p className="post-notes-preview">"{post.additional_notes}"</p>}
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        {currentView === 'post-tuition' && (
          <PostTuition
            currentUser={currentUser}
            token={token}
            API_URL={API_URL}
            setCurrentView={setCurrentView}
            openAuthModal={() => setIsAuthModalOpen(true)}
          />
        )}

        {currentView === 'my-posts' && (
          <MyTuitionPosts
            currentUser={currentUser}
            token={token}
            API_URL={API_URL}
            setCurrentView={setCurrentView}
            openAuthModal={() => setIsAuthModalOpen(true)}
          />
        )}

        {currentView === 'admin-dashboard' && (
          <AdminDashboard
            currentUser={currentUser}
            token={token}
            API_URL={API_URL}
            setCurrentView={setCurrentView}
            openAuthModal={() => setIsAuthModalOpen(true)}
          />
        )}

        {currentView === 'admin-users' && (
          <AdminUsers
            currentUser={currentUser}
            token={token}
            API_URL={API_URL}
            openAuthModal={() => setIsAuthModalOpen(true)}
          />
        )}

        {currentView === 'admin-posts' && (
          <AdminTuitionPosts
            currentUser={currentUser}
            token={token}
            API_URL={API_URL}
            openAuthModal={() => setIsAuthModalOpen(true)}
          />
        )}
      </main>

      <footer className="footer text-center">
        <p>&copy; 2026 Tuition Management Platform. End-to-End Implementation by Talha.</p>
      </footer>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
        API_URL={API_URL}
      />
    </div>
  )
}

export default App
