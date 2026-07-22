import React, { useState } from 'react'

function AuthModal({ isOpen, onClose, onLoginSuccess, API_URL }) {
  const [isLoginMode, setIsLoginMode] = useState(true)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    role: 'client'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/register'
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const data = await response.json()
      if (response.ok && data.success) {
        onLoginSuccess(data.user, data.token)
        onClose()
      } else {
        setError(data.error || data.message || 'Authentication failed.')
      }
    } catch (err) {
      setError('Unable to connect to backend server. Make sure Flask API is running on port 5000.')
    } finally {
      setLoading(false)
    }
  }

  // Quick Demo Logins for Viva & Evaluation convenience
  const handleQuickDemoLogin = async (demoRole, demoEmail) => {
    setLoading(true)
    setError('')

    try {
      let res = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: demoEmail, password: 'password123' })
      })
      let data = await res.json()

      // If account doesn't exist, auto-register it (unless admin)
      if ((!res.ok || !data.success) && demoRole !== 'admin') {
        res = await fetch(`${API_URL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: `Demo ${demoRole.toUpperCase()}`,
            email: demoEmail,
            password: 'password123',
            role: demoRole
          })
        })
        data = await res.json()
      }

      if (res.ok && data.success) {
        onLoginSuccess(data.user, data.token)
        onClose()
      } else {
        setError(data.error || 'Quick demo login failed.')
      }
    } catch (err) {
      setError('Backend connection error during quick demo login.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <h3>{isLoginMode ? '🔐 Sign In' : '📝 Register New Account'}</h3>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        {/* Quick Demo Login Buttons for Viva */}
        <div className="quick-demo-box">
          <p className="quick-demo-title">⚡ Quick Demo Logins (One-Click for Viva):</p>
          <div className="quick-demo-buttons">
            <button
              type="button"
              className="btn btn-demo btn-guardian"
              onClick={() => handleQuickDemoLogin('client', 'client@example.com')}
              disabled={loading}
            >
              👤 Client (Guardian/Student)
            </button>
            <button
              type="button"
              className="btn btn-demo btn-tutor"
              onClick={() => handleQuickDemoLogin('tutor', 'tutor@example.com')}
              disabled={loading}
            >
              📚 Tutor
            </button>
            <button
              type="button"
              className="btn btn-demo btn-admin"
              onClick={() => handleQuickDemoLogin('admin', 'admin@example.com')}
              disabled={loading}
            >
              ⚙️ Admin
            </button>
          </div>
        </div>

        <div className="modal-divider"><span>OR</span></div>

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLoginMode && (
            <>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g. Fahim Ahmed"
                  required
                />
              </div>

              <div className="form-group">
                <label>Phone Number (Optional)</label>
                <input
                  type="text"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="e.g. +8801712345678"
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="e.g. user@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />
          </div>

          {!isLoginMode && (
            <div className="form-group">
              <label>I am registering because:</label>
              <div className="role-options-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="role"
                    value="client"
                    checked={formData.role === 'client'}
                    onChange={handleChange}
                  />
                  <span>🙋‍♂️ I need a tutor (Client - Parent / Student)</span>
                </label>

                <label className="radio-label">
                  <input
                    type="radio"
                    name="role"
                    value="tutor"
                    checked={formData.role === 'tutor'}
                    onChange={handleChange}
                  />
                  <span>📚 I want to teach (Tutor)</span>
                </label>
              </div>
            </div>
          )}

          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? 'Processing...' : isLoginMode ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="modal-footer">
          <p>
            {isLoginMode ? "Don't have an account?" : "Already have an account?"}{' '}
            <button
              type="button"
              className="link-btn"
              onClick={() => {
                setIsLoginMode(!isLoginMode)
                setError('')
              }}
            >
              {isLoginMode ? 'Register here' : 'Sign in here'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

export default AuthModal
