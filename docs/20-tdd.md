# Tuition Management Platform - Technical Design Document (TDD)

## Folder Structure
```
tuition-management-platform/
├── README.md
├── package.json
├── server.js (API Server Entrypoint)
├── public/ (Static Frontend Assets)
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── docs/ (Course Documentation Files)
└── config/
    └── database.js
```

## Security Design
1. **Password Hashing:** Use `bcryptjs` on the server before inserting password records.
2. **Session Security:** Issue JWT tokens on login. Store them in localStorage or HTTP-only cookies.
3. **API Access Control:** Express middleware checks the token and roles (`req.user.role`) before granting access to specific endpoints (e.g., Admin dashboard, Apply).
