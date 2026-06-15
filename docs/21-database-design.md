# Tuition Management Platform - Database Design

## Relational Schema (DDL)

```sql
-- Create USERS table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('Admin', 'Tutor', 'Guardian')) NOT NULL
);

-- Create TUTOR_PROFILES table
CREATE TABLE tutor_profiles (
    user_id INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    education VARCHAR(255),
    institution VARCHAR(255),
    subjects TEXT, -- Comma-separated or JSON list
    experience TEXT,
    preferred_area VARCHAR(100),
    expected_salary DECIMAL(10, 2),
    bio TEXT,
    profile_photo VARCHAR(255)
);

-- Create TUITION_POSTS table
CREATE TABLE tuition_posts (
    id SERIAL PRIMARY KEY,
    guardian_id INT REFERENCES users(id) ON DELETE CASCADE,
    class VARCHAR(50) NOT NULL,
    subjects VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    tutor_gender VARCHAR(10) CHECK (tutor_gender IN ('Male', 'Female', 'Any')) DEFAULT 'Any',
    teaching_mode VARCHAR(20) CHECK (teaching_mode IN ('Online', 'Offline')) DEFAULT 'Offline',
    days_per_week INT NOT NULL,
    notes TEXT,
    status VARCHAR(20) CHECK (status IN ('Open', 'Closed')) DEFAULT 'Open'
);

-- Create APPLICATIONS table
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    tuition_post_id INT REFERENCES tuition_posts(id) ON DELETE CASCADE,
    tutor_id INT REFERENCES users(id) ON DELETE CASCADE,
    application_message TEXT,
    status VARCHAR(20) CHECK (status IN ('Pending', 'Accepted', 'Rejected')) DEFAULT 'Pending',
    UNIQUE(tuition_post_id, tutor_id) -- Prevent duplicate applications
);

-- Create REVIEWS table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    tutor_id INT REFERENCES users(id) ON DELETE CASCADE,
    guardian_id INT REFERENCES users(id) ON DELETE CASCADE,
    rating INT CHECK (rating BETWEEN 1 AND 5) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
