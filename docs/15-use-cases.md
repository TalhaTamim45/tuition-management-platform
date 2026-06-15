# Tuition Management Platform - Use Cases

## Use Case 1: Post Tuition Requirement
- **Actor:** Guardian
- **Description:** A guardian publishes their tutoring requirements to the public board.
- **Preconditions:** Guardian is logged in.
- **Basic Flow:**
  1. Guardian navigates to "Create Tuition Post".
  2. Input fields (Class, subjects, salary, location, preferred gender) are filled out.
  3. Guardian submits form.
  4. System validates inputs and saves to `tuition_posts` table.
  5. Post is displayed in the "Tuition Jobs" board.
- **Alternative Flow:**
  - 3a. Invalid inputs (e.g., negative salary): System highlights errors and prompts correction.

## Use Case 2: Apply for Job
- **Actor:** Tutor
- **Description:** A tutor applies to an active tuition post.
- **Preconditions:** Tutor is logged in and has completed their profile.
- **Basic Flow:**
  1. Tutor browses open jobs.
  2. Tutor clicks "Apply" on a post.
  3. Tutor submits application message.
  4. System saves status as "Pending" in the `applications` table.
