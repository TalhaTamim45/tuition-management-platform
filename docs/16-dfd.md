# Tuition Management Platform - Data Flow Diagram (DFD)

## Level 0 DFD (Context Diagram)
The Level 0 DFD shows the boundaries of the Tuition Management Platform and its interactions with external entities.

```mermaid
graph TD
    Guardian((Guardian)) -- Post Jobs, Review Tutors --> System[Tuition Management Platform]
    Tutor((Tutor)) -- Update Profile, Apply to Jobs --> System
    Admin((Admin)) -- Moderate Users, Delete Posts --> System
    System -- Show Applicants, Status Updates --> Guardian
    System -- Show Job Board, Application Status --> Tutor
    System -- User Lists, Reports, Stats --> Admin
```

## Level 1 DFD (Process Level Diagram)
The Level 1 DFD breaks down the main processes of the platform: Authentication, Profile Management, Job Posting, Application Flow, and Admin Moderation.

```mermaid
graph TD
    subgraph Processes
        P1[1.0 Auth Process]
        P2[2.0 Profile Manager]
        P3[3.0 Job Posting Engine]
        P4[4.0 Application Manager]
        P5[5.0 Admin Moderator]
    end

    subgraph Data Stores
        D1[(users)]
        D2[(tutor_profiles)]
        D3[(tuition_posts)]
        D4[(applications)]
    end

    Tutor -- Credentials --> P1
    Guardian -- Credentials --> P1
    P1 -- Save/Verify --> D1

    Tutor -- Profile Info --> P2
    P2 -- Update --> D2

    Guardian -- Job Details --> P3
    P3 -- Create/Update --> D3

    Tutor -- Applications --> P4
    P4 -- Submit --> D4
    D4 -- Fetch applicants --> Guardian
    Guardian -- Accept/Reject --> P4

    Admin -- Block/Delete commands --> P5
    P5 -- Modify --> D1
    P5 -- Modify --> D3
```
