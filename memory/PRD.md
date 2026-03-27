# Staylet - Product Requirements Document

## Original Problem Statement
Build a SaaS web app called Staylet that helps UK short-term let hosts track compliance records, expiry dates, required documents, and property admin.

## User Personas
- **Primary**: UK short-term let hosts with 1-15 properties
- **Use case**: Track compliance documents, certificates, and deadlines without spreadsheets
- **Pain points**: Missed renewals, scattered documents, manual tracking

## User Choices
- Design: Modern minimal (clean, premium B2B SaaS)
- Color: Blue primary (trust-first palette)
- Auth: JWT-based email/password (scalable for future social login)
- Password reset: Mocked for now (ready for email integration)

## Core Requirements (Static)
1. Public landing page with hero, benefits, pricing preview, FAQ
2. Email/password authentication (signup, login, logout, reset)
3. Protected app shell with sidebar navigation
4. Dashboard with real-time stats
5. Property CRUD with UK-specific fields
6. Compliance record tracking with status logic
7. Task management with recurring support
8. In-app notification system
9. MongoDB data models for all entities

## What's Been Implemented

### Phase 1 (March 27, 2026) - Foundation
- Landing page with hero, benefits, pricing, FAQ
- JWT authentication (signup, login, logout, reset mocked)
- App shell with sidebar navigation
- Dashboard with placeholder stats
- Empty state pages for all sections

### Phase 2 (March 27, 2026) - Compliance Tracking
- **Properties CRUD**: Create/Edit/Delete with UK fields
- **Property Detail Page**: Compliance summary, records list, tasks section
- **Compliance Records CRUD**: 10 categories, auto-status calculation
- **Quick Setup / Bulk Compliance Creation**: 9 templates, select all/clear
- **Status Logic**: compliant (>30d), expiring_soon (≤30d), overdue (past), missing
- **Dashboard with Real Data**: Counts matching actual DB data
- **Compliance Page**: List with filters by status/category

### Phase 2 Bug Fixes (March 27, 2026)
- Backend validation for empty/whitespace fields
- Frontend error handling improvements
- Accessibility: DialogDescription in all modals
- Mobile responsiveness: overflow-x-auto on tables

### Phase 3 (March 27, 2026) - Tasks & Reminder Automation
- **Tasks System**:
  - Full CRUD with title, description, due_date, priority, category
  - Status: pending → in_progress → completed
  - Priority levels: low, medium, high, urgent
  - Categories: general, maintenance, inspection, renewal, safety, seasonal, admin
  - Link tasks to specific properties
  - **Recurring Tasks**: daily, weekly, monthly, yearly patterns
  - When completing a recurring task, auto-creates next occurrence
  - 10 predefined task templates (Smoke Alarm Check, Insurance Renewal, etc.)

- **Tasks Page**:
  - All tasks view with stats (Overdue, Due Soon, Completed)
  - Filters: status (active/completed/all), priority, property
  - Task cards with badges for priority, status, recurring
  - Quick actions: Start Task, Mark Complete, Edit, Delete

- **Reminder Engine**:
  - Auto-generates notifications based on compliance expiry dates
  - Configurable lead times: 90, 60, 30, 14, 7 days before expiry
  - Overdue alerts for expired documents
  - Task due date reminders

- **In-App Notification System**:
  - Notification bell in header with unread count badge
  - Dropdown showing all notifications with types:
    - expiry_reminder (amber)
    - overdue_alert (red)
    - task_due (blue)
    - missing_record (slate)
  - Mark as read (individual and all)
  - Delete notifications
  - Click to navigate to relevant page

- **Notification Preferences (Settings)**:
  - In-app reminders toggle (on/off)
  - Email reminders toggle (MOCKED with "Coming soon" badge)
  - Reminder timing selector: 90, 60, 30, 14, 7 days
  - Preferences saved per user

- **Dashboard Improvements**:
  - **Overdue Alert Section**: Red prominent banner for items needing immediate attention
  - **Next 5 Expiries Card**: Shows upcoming expiries with countdown (X days)
  - **Tasks Due This Month Card**: Shows tasks with due dates this month
  - **Quick Actions**: Add Property, Add Compliance Record, Create Task

## Tech Stack
- React + Tailwind + Shadcn UI
- FastAPI + MongoDB (Motor async driver)
- JWT auth with bcrypt password hashing
- Outfit/Inter fonts, Blue (#2563EB) primary

## Prioritized Backlog

### P0 (Next)
- Document file upload and storage (attach files to compliance records)
- Export/download compliance certificates

### P1 (Future)
- Real email sending for password reset & expiry notifications
- Stripe billing integration
- Team access/multi-user support

### P2 (Later)
- Social login (Google)
- Mobile app or PWA
- API access for Business tier
- Reporting and analytics dashboard

## Next Tasks
1. Integrate document file upload (object storage)
2. Add email notifications via SendGrid/Resend
3. Implement Stripe billing integration
4. Build team member invite system

## Mocked Functionality
- **Password Reset**: Returns success message without actually sending email
- **Email Reminders**: UI toggle exists with "Coming soon" badge, preference is saved but no actual email sending

## Key API Endpoints

### Auth
- POST `/api/auth/signup`, `/api/auth/login`
- POST `/api/auth/forgot-password`, `/api/auth/reset-password`

### Properties
- GET/POST `/api/properties`
- GET/PUT/DELETE `/api/properties/{id}`

### Compliance
- GET/POST `/api/compliance-records`
- PUT/DELETE `/api/compliance-records/{id}`
- POST `/api/compliance-records/bulk`

### Tasks
- GET/POST `/api/tasks`
- PUT/DELETE `/api/tasks/{id}`
- GET `/api/tasks/templates`

### Notifications
- GET `/api/notifications`
- GET `/api/notifications/generate`
- PUT `/api/notifications/{id}/read`
- PUT `/api/notifications/read-all`
- DELETE `/api/notifications/{id}`

### User Preferences
- GET/PUT `/api/user/preferences`

### Dashboard
- GET `/api/dashboard/stats`
- GET `/api/dashboard/data`

## Database Collections
- `users`: email, hashed_password, full_name
- `properties`: name, address, postcode, uk_nation, property_type, etc.
- `compliance_records`: property_id, title, category, status, expiry_date, etc.
- `tasks`: title, description, due_date, priority, status, property_id, is_recurring, recurrence_pattern
- `notifications`: user_id, type, title, message, reference_type, reference_id, is_read
- `user_preferences`: user_id, email_reminders, inapp_reminders, reminder_lead_days
