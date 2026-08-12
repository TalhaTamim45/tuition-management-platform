import React, { useState, useEffect } from 'react'

function UserProfile({ currentUser, token, API_URL, onProfileUpdate, openAuthModal }) {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    education: '',
    institution: '',
    subjects: '',
    experience: '',
    salary_expectation: '0',
    address: ''
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (currentUser) {
      setFormData({
        name: currentUser.name || '',
        phone: currentUser.phone || '',
        education: currentUser.education || '',
        institution: currentUser.institution || '',
        subjects: currentUser.subjects || '',
        experience: currentUser.experience || '',
        salary_expectation: currentUser.salary_expectation !== undefined ? String(currentUser.salary_expectation) : '0',
        address: currentUser.address || ''
      })
    }
  }, [currentUser])

  if (!currentUser) {
    return (
      <div className="card text-center p-5 auth-guard-card">
        <h2>👤 My Profile</h2>
        <p className="lead">Please log in to manage your profile details.</p>
        <div className="mt-4">
          <button className="btn btn-primary btn-lg" onClick={openAuthModal}>
            Sign In / Register
          </button>
        </div>
      </div>
    )
  }

  const isTutor = currentUser.role?.toLowerCase() === 'tutor'

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setError('')
    setSuccess('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    const salaryNum = parseFloat(formData.salary_expectation)
    if (isNaN(salaryNum) || salaryNum < 0) {
      setError('Salary expectation must be a valid positive number.')
      setLoading(false)
      return
    }

    try {
      const response = await fetch(`${API_URL}/api/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: formData.name.trim(),
          phone: formData.phone.trim(),
          education: formData.education.trim(),
          institution: formData.institution.trim(),
          subjects: formData.subjects.trim(),
          experience: formData.experience.trim(),
          salary_expectation: salaryNum,
          address: formData.address.trim()
        })
      })

      const data = await response.json()
      if (response.ok && data.success) {
        setSuccess('🎉 Profile updated successfully!')
        if (typeof onProfileUpdate === 'function') {
          onProfileUpdate(data.user)
        }
      } else {
        setError(data.error || data.message || 'Failed to update profile.')
      }
    } catch (err) {
      setError('Network error. Unable to save profile changes.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="user-profile-container card" style={{ maxWidth: '650px', margin: '0 auto' }}>
      <div className="form-header">
        <h2>👤 Manage Profile</h2>
        <p className="subtitle">Update your personal and professional qualifications to match with users.</p>
      </div>

      {success && <div className="alert alert-success">{success}</div>}
      {error && <div className="alert alert-danger">⚠️ {error}</div>}

      <form onSubmit={handleSubmit} className="profile-form">
        <div className="form-group">
          <label>Email Address (Read-only)</label>
          <input
            type="email"
            value={currentUser.email}
            disabled
            style={{ cursor: 'not-allowed', background: '#e2e8f0', color: '#64748b' }}
          />
        </div>

        <div className="form-row grid-2">
          <div className="form-group">
            <label>Full Name <span className="required">*</span></label>
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
            <label>Phone Number</label>
            <input
              type="text"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="e.g. +8801712345678"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Address</label>
          <input
            type="text"
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="e.g. Dhanmondi, Dhaka"
          />
        </div>

        {isTutor && (
          <fieldset style={{ border: '1px solid var(--border)', padding: '1.25rem', borderRadius: '8px', marginBottom: '1.5rem', background: '#fafafa' }}>
            <legend style={{ padding: '0 0.5rem', fontWeight: '700', fontSize: '0.85rem', color: 'var(--primary)', textTransform: 'uppercase' }}>
              📚 Tutor Professional Info
            </legend>

            <div className="form-row grid-2" style={{ marginTop: '0.5rem' }}>
              <div className="form-group">
                <label>Highest Education</label>
                <input
                  type="text"
                  name="education"
                  value={formData.education}
                  onChange={handleChange}
                  placeholder="e.g. B.Sc in EEE, HSC Candidate"
                />
              </div>

              <div className="form-group">
                <label>Institution</label>
                <input
                  type="text"
                  name="institution"
                  value={formData.institution}
                  onChange={handleChange}
                  placeholder="e.g. BUET, Dhaka University"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Subjects you can teach</label>
              <input
                type="text"
                name="subjects"
                value={formData.subjects}
                onChange={handleChange}
                placeholder="e.g. Mathematics, Physics, Chemistry"
              />
            </div>

            <div className="form-row grid-2">
              <div className="form-group">
                <label>Tuition Experience</label>
                <input
                  type="text"
                  name="experience"
                  value={formData.experience}
                  onChange={handleChange}
                  placeholder="e.g. 2 Years, No Experience"
                />
              </div>

              <div className="form-group">
                <label>Salary Expectation (BDT ৳/month)</label>
                <input
                  type="number"
                  name="salary_expectation"
                  value={formData.salary_expectation}
                  onChange={handleChange}
                  placeholder="e.g. 6000"
                  min="0"
                />
              </div>
            </div>
          </fieldset>
        )}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={loading}>
            {loading ? <><span className="spinner"></span> Saving Profile...</> : '💾 Save Profile Details'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default UserProfile
