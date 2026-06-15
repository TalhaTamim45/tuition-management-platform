# Tuition Management Platform - Acceptance Criteria

## Acceptance Criteria for Core User Stories

### US-03: Create Tuition Post
- **Scenario:** Guardian successfully posts a tuition job.
  - **Given:** The user is logged in as a "Guardian".
  - **When:** They navigate to the "Create Post" page, fill in all required fields (Class, Subjects, Location, Salary, Days/Week), and click "Post".
  - **Then:** The system validates the input, saves it to the database, and displays a "Post Created Successfully" message.
  - **And:** The post is instantly visible in the public "Tuition Jobs" list.

### US-05: Apply for Tuition Job
- **Scenario:** Tutor successfully applies for a job.
  - **Given:** The user is logged in as a "Tutor" and has a complete profile.
  - **When:** They click the "Apply" button on an active tuition post.
  - **Then:** The system creates an application record with "Pending" status and alerts the tutor.
  - **And:** The tutor cannot apply to the same post twice.
