# Tuition Management Platform - Non-Functional Requirements

## Non-Functional Requirements List

### 1. Security & Authentication
- **NFR-01:** Passwords must be hashed using bcrypt before database storage.
- **NFR-02:** API endpoints must be secured using JWT (JSON Web Tokens) to restrict role access.

### 2. Performance
- **NFR-03:** Homepage and dashboards must load in less than 2.0 seconds under normal network conditions.
- **NFR-04:** Database queries for search/filter operations must execute in less than 200ms.

### 3. Reliability & Availability
- **NFR-05:** The system should have an uptime of 99.9% during academic semesters.
- **NFR-06:** Graceful error handling: API errors should not crash the frontend UI.

### 4. Usability
- **NFR-07:** The website must be fully responsive, supporting smartphones, tablets, and desktops.
