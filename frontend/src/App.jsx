import React from 'react'

function App() {
  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-logo">🎓 Tuition Management Platform</div>
        <div className="nav-links">
          <a href="#home">Home</a>
          <a href="#login">Login</a>
          <a href="#register">Register</a>
          <a href="#jobs">Tuition Jobs</a>
        </div>
      </nav>

      <header className="hero-section">
        <h1>Tuition Management Platform</h1>
        <p className="subtitle">Find tutors and tuition jobs in one place</p>
        <div className="btn-group">
          <button className="btn btn-primary" onClick={() => alert('Search feature coming soon!')}>Find Tuition Jobs</button>
          <button className="btn btn-secondary" onClick={() => alert('Posting feature coming soon!')}>Post Tuition Needs</button>
        </div>
      </header>
      
      <main className="features-grid">
        <div className="feature-card">
          <h3>For Tutors</h3>
          <p>Create a verified academic profile, select your preferred subjects/areas, set your salary, and apply to tuition vacancies without agent commissions.</p>
        </div>
        <div className="feature-card">
          <h3>For Guardians</h3>
          <p>Post your home or online tuition requirements, review tutor applications, verify credentials, and rate tutors after completion.</p>
        </div>
        <div className="feature-card">
          <h3>Safe & Secure</h3>
          <p>Strict role-based authorization, fake post moderation, and direct tutor-to-guardian connection.</p>
        </div>
      </main>

      <footer className="footer">
        <p>&copy; 2026 Tuition Management Platform (Group-S5-13). All rights reserved.</p>
      </footer>
    </div>
  )
}

export default App
