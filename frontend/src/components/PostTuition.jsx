import React, { useState } from 'react'

function PostTuition({ currentUser, token, API_URL, setCurrentView, openAuthModal }) {
  const [formData, setFormData] = useState({
    title: '',
    student_class: '',
    subjects: '',
    location: '',
    monthly_salary: '',
    preferred_tutor_gender: 'Any',
    teaching_mode: 'Offline',
    days_per_week: '4',
    additional_notes: ''
  })

  const [fieldErrors, setFieldErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [serverError, setServerError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  // 1. Guard check: Only logged-in Guardians or Students can post
  if (!currentUser) {
    return (
      <div className="card text-center p-5 auth-guard-card">
        <h2>🔒 Login Required</h2>
        <p className="lead">You must be logged in as a <strong>Guardian</strong> or <strong>Student</strong> to post a tuition job requirement.</p>
        <div className="mt-4">
          <button className="btn btn-primary btn-lg" onClick={openAuthModal}>
            Sign In / Register Now
          </button>
        </div>
      </div>
    )
  }

  if (currentUser.role !== 'Guardian' && currentUser.role !== 'Student') {
    return (
      <div className="card text-center p-5 auth-guard-card">
        <h2>🚫 Access Restricted</h2>
        <p className="lead">
          Your current account role is <strong>{currentUser.role}</strong>. Only <strong>Guardian</strong> or <strong>Student</strong> accounts are permitted to post tuition jobs.
        </p>
        <p className="text-muted">If you are a Guardian or Student, please switch accounts or register a new Guardian profile.</p>
        <div className="mt-4">
          <button className="btn btn-secondary" onClick={openAuthModal}>
            Switch Account
          </button>
        </div>
      </div>
    )
  }

  // Handle Input Changes & Clear Field Errors
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    // Clear error for specific field as user types
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: '' }))
    }
    setServerError('')
  }

  // Client-side Validation Logic
  const validateForm = () => {
    const errors = {}

    if (!formData.title.trim()) {
      errors.title = 'Tuition title is required.'
    }

    if (!formData.student_class.trim()) {
      errors.student_class = 'Student class is required.'
    }

    if (!formData.subjects.trim()) {
      errors.subjects = 'Subjects are required.'
    }

    if (!formData.location.trim()) {
      errors.location = 'Location is required.'
    }

    const salaryNum = parseFloat(formData.monthly_salary)
    if (!formData.monthly_salary) {
      errors.monthly_salary = 'Monthly salary is required.'
    } else if (isNaN(salaryNum) || salaryNum <= 0) {
      errors.monthly_salary = 'Monthly salary must be a positive number.'
    }

    if (!formData.teaching_mode) {
      errors.teaching_mode = 'Teaching mode is required.'
    } else if (!['Online', 'Offline'].includes(formData.teaching_mode)) {
      errors.teaching_mode = 'Teaching mode must be either Online or Offline.'
    }

    const daysNum = parseInt(formData.days_per_week, 10)
    if (!formData.days_per_week) {
      errors.days_per_week = 'Days per week is required.'
    } else if (isNaN(daysNum) || daysNum < 1 || daysNum > 7) {
      errors.days_per_week = 'Days per week must be between 1 and 7.'
    }

    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  // Form Submission Handler
  const handleSubmit = async (e) => {
    e.preventDefault()
    setServerError('')
    setSuccessMessage('')

    // Perform client validation first
    if (!validateForm()) {
      return
    }

    setLoading(true)

    const payload = {
      title: formData.title.trim(),
      student_class: formData.student_class.trim(),
      subjects: formData.subjects.trim(),
      location: formData.location.trim(),
      monthly_salary: parseFloat(formData.monthly_salary),
      preferred_tutor_gender: formData.preferred_tutor_gender,
      teaching_mode: formData.teaching_mode,
      days_per_week: parseInt(formData.days_per_week, 10),
      additional_notes: formData.additional_notes.trim()
    }

    try {
      const response = await fetch(`${API_URL}/api/tuition-posts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setSuccessMessage('🎉 Tuition post created successfully! Redirecting to My Tuition Posts...')
        // Clear form
        setFormData({
          title: '',
          student_class: '',
          subjects: '',
          location: '',
          monthly_salary: '',
          preferred_tutor_gender: 'Any',
          teaching_mode: 'Offline',
          days_per_week: '4',
          additional_notes: ''
        })

        // Redirect after 1.5 seconds
        setTimeout(() => {
          setCurrentView('my-posts')
        }, 1500)
      } else {
        if (data.errors) {
          setFieldErrors(data.errors)
        }
        setServerError(data.message || data.error || 'Failed to submit tuition post.')
      }
    } catch (err) {
      setServerError('Network error. Unable to connect to the backend server.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="post-tuition-container card">
      <div className="form-header">
        <h2>📌 Post a Tuition Job Requirement</h2>
        <p className="subtitle">Fill out the form below to connect with qualified home and online tutors.</p>
      </div>

      {/* Global Success & Error Banners */}
      {successMessage && (
        <div className="alert alert-success">
          {successMessage}
        </div>
      )}

      {serverError && (
        <div className="alert alert-danger">
          ⚠️ {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate className="tuition-form">
        {/* Tuition Title */}
        <div className="form-group">
          <label htmlFor="title">Tuition Title <span className="required">*</span></label>
          <input
            id="title"
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g. Need Class 9 Higher Math & Physics Tutor"
            className={fieldErrors.title ? 'input-error' : ''}
          />
          {fieldErrors.title && <span className="field-error">{fieldErrors.title}</span>}
        </div>

        <div className="form-row grid-2">
          {/* Student Class */}
          <div className="form-group">
            <label htmlFor="student_class">Student Class <span className="required">*</span></label>
            <input
              id="student_class"
              type="text"
              name="student_class"
              value={formData.student_class}
              onChange={handleChange}
              placeholder="e.g. Class 9, HSC 1st Year, O-Level"
              className={fieldErrors.student_class ? 'input-error' : ''}
            />
            {fieldErrors.student_class && <span className="field-error">{fieldErrors.student_class}</span>}
          </div>

          {/* Subjects */}
          <div className="form-group">
            <label htmlFor="subjects">Subjects <span className="required">*</span></label>
            <input
              id="subjects"
              type="text"
              name="subjects"
              value={formData.subjects}
              onChange={handleChange}
              placeholder="e.g. General Math, Physics, Chemistry"
              className={fieldErrors.subjects ? 'input-error' : ''}
            />
            {fieldErrors.subjects && <span className="field-error">{fieldErrors.subjects}</span>}
          </div>
        </div>

        <div className="form-row grid-2">
          {/* Location */}
          <div className="form-group">
            <label htmlFor="location">Location <span className="required">*</span></label>
            <input
              id="location"
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g. Dhanmondi, Dhaka"
              className={fieldErrors.location ? 'input-error' : ''}
            />
            {fieldErrors.location && <span className="field-error">{fieldErrors.location}</span>}
          </div>

          {/* Monthly Salary */}
          <div className="form-group">
            <label htmlFor="monthly_salary">Monthly Salary (BDT ৳) <span className="required">*</span></label>
            <input
              id="monthly_salary"
              type="number"
              name="monthly_salary"
              value={formData.monthly_salary}
              onChange={handleChange}
              placeholder="e.g. 8000"
              min="1"
              step="100"
              className={fieldErrors.monthly_salary ? 'input-error' : ''}
            />
            {fieldErrors.monthly_salary && <span className="field-error">{fieldErrors.monthly_salary}</span>}
          </div>
        </div>

        <div className="form-row grid-3">
          {/* Preferred Tutor Gender */}
          <div className="form-group">
            <label htmlFor="preferred_tutor_gender">Preferred Tutor Gender</label>
            <select
              id="preferred_tutor_gender"
              name="preferred_tutor_gender"
              value={formData.preferred_tutor_gender}
              onChange={handleChange}
            >
              <option value="Any">Any Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>

          {/* Teaching Mode */}
          <div className="form-group">
            <label htmlFor="teaching_mode">Teaching Mode <span className="required">*</span></label>
            <select
              id="teaching_mode"
              name="teaching_mode"
              value={formData.teaching_mode}
              onChange={handleChange}
              className={fieldErrors.teaching_mode ? 'input-error' : ''}
            >
              <option value="Offline">Offline (In-Person Home Tutoring)</option>
              <option value="Online">Online (Remote / Zoom / Google Meet)</option>
            </select>
            {fieldErrors.teaching_mode && <span className="field-error">{fieldErrors.teaching_mode}</span>}
          </div>

          {/* Days Per Week */}
          <div className="form-group">
            <label htmlFor="days_per_week">Days Per Week (1 to 7) <span className="required">*</span></label>
            <input
              id="days_per_week"
              type="number"
              name="days_per_week"
              value={formData.days_per_week}
              onChange={handleChange}
              min="1"
              max="7"
              className={fieldErrors.days_per_week ? 'input-error' : ''}
            />
            {fieldErrors.days_per_week && <span className="field-error">{fieldErrors.days_per_week}</span>}
          </div>
        </div>

        {/* Additional Notes */}
        <div className="form-group">
          <label htmlFor="additional_notes">Additional Notes / Requirements (Optional)</label>
          <textarea
            id="additional_notes"
            name="additional_notes"
            rows="3"
            value={formData.additional_notes}
            onChange={handleChange}
            placeholder="e.g. Prefer BUET/DU tutors, tutoring time around 5 PM to 7 PM."
          />
        </div>

        {/* Submit Button & Loading State */}
        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary btn-lg btn-submit"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span> Submitting Job Post...
              </>
            ) : (
              '🚀 Publish Tuition Job'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default PostTuition
