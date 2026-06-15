# Tuition Management Platform - API Design

## Endpoints Specification

### 1. Authentication Endpoints

#### POST `/api/auth/register`
- **Description:** Registers a new user.
- **Request Body:**
  ```json
  {
    "name": "Fahim Ahmed",
    "email": "fahim@example.com",
    "phone": "+8801712345678",
    "password": "securepassword",
    "role": "Tutor"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "message": "User registered successfully",
    "userId": 12
  }
  ```

### 2. Tuition Post Endpoints

#### GET `/api/posts`
- **Description:** Get all active tuition postings.
- **Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "class": "9",
      "subjects": "Math, Physics",
      "location": "Mirpur, Dhaka",
      "salary": "8000.00",
      "tutor_gender": "Male",
      "days_per_week": 4,
      "status": "Open"
    }
  ]
  ```

#### POST `/api/posts`
- **Description:** Create a new tuition job post (Guardian only).
- **Headers:** `Authorization: Bearer <JWT_TOKEN>`
- **Request Body:**
  ```json
  {
    "class": "9",
    "subjects": "Math, Physics",
    "location": "Mirpur, Dhaka",
    "salary": 8000,
    "tutor_gender": "Male",
    "teaching_mode": "Offline",
    "days_per_week": 4,
    "notes": "Need tutor from BUET/DU."
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "message": "Tuition post created successfully",
    "postId": 45
  }
  ```
