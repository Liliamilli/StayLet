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
- Document extraction: OpenAI GPT-4o vision

## Core Requirements (Static)
1. Public landing page with hero, benefits, pricing preview, FAQ
2. Email/password authentication (signup, login, logout, reset)
3. Protected app shell with sidebar navigation
4. Dashboard with real-time stats
5. Property CRUD with UK-specific fields
6. Compliance record tracking with status logic
7. Task management with recurring support
8. In-app notification system
9. Document upload with AI extraction
10. MongoDB data models for all entities

## What's Been Implemented

### Phase 1 - Foundation
- Landing page with hero, benefits, pricing, FAQ
- JWT authentication (signup, login, logout, reset mocked)
- App shell with sidebar navigation
- Dashboard with placeholder stats

### Phase 2 - Compliance Tracking
- Properties CRUD with UK fields
- Property Detail Page with compliance summary
- Compliance Records CRUD with 10 categories
- Quick Setup / Bulk Compliance Creation
- Status Logic: compliant, expiring_soon, overdue, missing
- Dashboard with real counts

### Phase 3 - Tasks & Reminder Automation
- Tasks CRUD with recurring support (daily/weekly/monthly/yearly)
- 10 predefined task templates
- Tasks Page with filters (status, priority, property)
- Reminder Engine generating notifications based on expiry dates
- In-App Notification System with bell icon and dropdown
- Notification Preferences in Settings
- Dashboard: Overdue alert section, Next 5 Expiries, Tasks Due This Month

### Phase 4 - Document Upload & Extraction (March 27, 2026)
- **File Upload System**:
  - Accepts PDF, PNG, JPG files up to 10MB
  - Files stored in `/app/backend/uploads/`
  - Document metadata stored in MongoDB

- **Document Management**:
  - Upload documents to compliance records
  - Download original files
  - Delete documents (removes from disk and database)
  - Link documents to compliance records

- **Smart AI Extraction (GPT-4o Vision)**:
  - Automatic document type detection
  - Issue date extraction
  - Expiry date extraction
  - Confidence indicators (HIGH/MEDIUM/LOW)
  - Fallback to filename-based category suggestion

- **Extraction Review Flow**:
  - Shows extracted values with confidence badges
  - "Suggested" labels for AI-detected values
  - User can edit any value before saving
  - Clear messaging: "AI-powered extraction • Results may vary • Always verify dates"

- **Upload-First Shortcut**:
  - "Upload Document" button on property detail page
  - Upload file → AI extraction → Review form → Create compliance record
  - Document automatically linked to new record

- **UI Components**:
  - DocumentUpload: Dropzone with drag-and-drop
  - ExtractionReview: Form with confidence indicators
  - DocumentList: File cards with download/delete
  - UploadDocumentModal: Combined upload + review workflow

## Tech Stack
- React + Tailwind + Shadcn UI
- FastAPI + MongoDB (Motor async driver)
- JWT auth with bcrypt password hashing
- OpenAI GPT-4o for document extraction (via emergentintegrations)
- Outfit/Inter fonts, Blue (#2563EB) primary

## Prioritized Backlog

### P0 (Next)
- Show uploaded documents on compliance record cards
- Document preview for images and PDFs

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
1. Display uploaded documents on compliance record detail view
2. Add inline document preview (images and PDF first page)
3. Implement real email notifications via SendGrid/Resend
4. Build Stripe billing integration

## Mocked Functionality
- **Password Reset**: Returns success message without actually sending email
- **Email Reminders**: UI toggle exists with "Coming soon" badge, preference saved but no actual email

## Key API Endpoints

### Documents
- POST `/api/documents/upload` - Upload file (optional compliance_record_id to link)
- POST `/api/documents/upload-and-extract` - Upload + AI extraction
- GET `/api/documents/{id}` - Get document metadata
- GET `/api/documents/{id}/download` - Download file
- PUT `/api/documents/{id}/link` - Link document to compliance record
- DELETE `/api/documents/{id}` - Delete document
- GET `/api/compliance-records/{record_id}/documents` - Get record's documents

### Other Endpoints (Previous Phases)
- Auth: `/api/auth/signup`, `/api/auth/login`, `/api/auth/forgot-password`
- Properties: `/api/properties`, `/api/properties/{id}`
- Compliance: `/api/compliance-records`, `/api/compliance-records/{id}`, `/api/compliance-records/bulk`
- Tasks: `/api/tasks`, `/api/tasks/{id}`, `/api/tasks/templates`
- Notifications: `/api/notifications`, `/api/notifications/generate`, `/api/notifications/{id}/read`
- User Preferences: `/api/user/preferences`
- Dashboard: `/api/dashboard/stats`, `/api/dashboard/data`

## Database Collections
- `users`: email, hashed_password, full_name
- `properties`: name, address, postcode, uk_nation, property_type, etc.
- `compliance_records`: property_id, title, category, status, expiry_date, etc.
- `tasks`: title, description, due_date, priority, status, property_id, is_recurring
- `notifications`: user_id, type, title, message, reference_type, reference_id, is_read
- `user_preferences`: user_id, email_reminders, inapp_reminders, reminder_lead_days
- `documents`: id, user_id, compliance_record_id, filename, original_filename, file_type, file_size, uploaded_at

## File Storage
- Upload directory: `/app/backend/uploads/`
- Allowed types: PDF, PNG, JPG
- Max size: 10MB
- Filename format: `{uuid}.{extension}`
