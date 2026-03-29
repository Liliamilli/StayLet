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

### Phase 4 Stabilization (March 27, 2026)
- Verified all form validation working correctly (property, compliance, task modals)
- Verified database writes functioning properly
- Verified data refresh after CRUD operations
- Verified mobile layout (375px) displays correctly
- Verified navigation and sidebar work correctly
- Verified status badges show correct colors (compliant/expiring_soon/overdue)
- Verified dashboard counts match actual database data
- **All 24 backend tests + frontend UI tests passed (100%)**

### Phase 5 - Subscription Billing (March 27, 2026)
- **Subscription Plans**:
  - Solo: £19/month (£190/year), 1 property limit
  - Portfolio: £39/month (£390/year), 5 properties limit
  - Operator: £79/month (£790/year), 15 properties limit

- **Free Trial System**:
  - 14-day free trial on signup
  - Default plan: Solo
  - Trial status shown in dashboard and billing page
  - Trial countdown banner with "Upgrade Now" CTA

- **Plan Limit Enforcement**:
  - Property limit checked before creating new property
  - UpgradePlanModal shown when limit reached
  - Clear messaging about current limit and upgrade options
  - Downgrade blocked if property count exceeds new plan limit

- **Billing Page**:
  - Current subscription display (plan, status, properties, price)
  - All 3 plan cards with upgrade/downgrade buttons
  - **Monthly/Annual pricing toggle** with "Save 17%" badge
  - Annual view shows equivalent monthly price and yearly savings per plan
  - Trial banner with countdown
  - Billing history placeholder
  - Payment method placeholder (Stripe ready)

- **Landing Page Pricing**:
  - Premium 3-column pricing cards
  - "Most Popular" badge on Portfolio plan
  - **Monthly/Annual pricing toggle** with "Save 17%" badge
  - Dynamic pricing display based on toggle selection
  - Per-plan savings badges (e.g., "Save £78/yr" on Portfolio)
  - Feature comparison for each plan

- **Subscription APIs**:
  - GET `/api/subscription` - Current subscription details
  - GET `/api/subscription/plans` - All available plans
  - GET `/api/subscription/check-limit` - Check if can add property
  - POST `/api/subscription/change` - Upgrade/downgrade plan

## Tech Stack
- React + Tailwind + Shadcn UI
- FastAPI + MongoDB (Motor async driver)
- JWT auth with bcrypt password hashing
- OpenAI GPT-4o for document extraction (via emergentintegrations)
- Outfit/Inter fonts, Blue (#2563EB) primary

## Prioritized Backlog

### P0 (Next)
- ~~Integrate Stripe for actual payment processing~~ ✅ COMPLETED
- ~~Show uploaded documents on compliance record cards~~ ✅ COMPLETED
- ~~Document preview for images and PDFs~~ ✅ COMPLETED

### P1 (Future)
- Real email sending for password reset & expiry notifications
- Team access/multi-user support

### P2 (Later)
- Social login (Google)
- Mobile app or PWA
- API access for Business tier
- Reporting and analytics dashboard

### Onboarding and Demo Mode (March 27, 2026)
- **Demo Mode** (`/api/auth/demo`):
  - One-click demo from landing page "Try Demo Mode" button
  - Creates temporary demo account with Portfolio plan
  - Seeds 3 realistic UK properties:
    - Victoria Terrace Apartment (London, SW1V 1AA)
    - Cotswold Cottage (Cotswolds, GL54 2HN)
    - Edinburgh Old Town Flat (Scotland, EH1 1QS)
  - Seeds 12 compliance records with mixed statuses (compliant, expiring_soon, overdue)
  - Seeds 6 tasks with varied priorities and due dates
  - Purple "Demo Mode" banner with "Start Free Trial" CTA

- **Onboarding Wizard** (`OnboardingWizard.js`):
  - Appears after signup for new users
  - 3-step guided onboarding:
    1. Add your first property
    2. Add a compliance record
    3. See your dashboard
  - Progress bar showing completion percentage
  - Skip functionality (X button or "Skip for now" link)
  - Tracks completion via `/api/user/onboarding` endpoints

- **Improved Empty States** (`EmptyState.js`):
  - New `variant="featured"` with gradient background
  - Tips and hints to help users get started
  - Context-specific messaging for each page
  - Dashboard: "Most hosts add their first property in under 15 minutes"
  - Properties: "Track specific requirements for England, Scotland, Wales, or Northern Ireland"
  - Tasks: "Use recurring tasks for annual inspections"
  - Compliance: "Smart document extraction can read PDFs automatically"

### Landing Page Conversion Redesign (March 27, 2026)
- **Hero Section**: New headline "Stop chasing certificates. Start staying compliant."
  - Trust badge "Built for UK short-let hosts"
  - Clear value proposition copy
  - Dual CTA: "Start Your Free Trial" + "Try Demo Mode"
  - Trust signals row (UK-based, GDPR, Encrypted, 99.9% Uptime)

- **Problem Section**: Dark background with pain points
  - Expired certificates you forgot about
  - Scattered documents everywhere
  - Manual calendar reminders
  - No clear view across properties

- **How It Works**: 3-step process
  - Add properties → Upload documents → Stay ahead of deadlines

- **Benefits Section**: 4 cards with stats
  - Never miss a renewal (90 days advance warning)
  - One place for everything (100% coverage)
  - Always audit-ready (<30 sec to find documents)
  - See all properties at once (1-15 properties supported)

- **Features Grid**: 6 feature highlights
  - Smart document extraction, UK compliance built-in, Task management
  - Secure cloud storage, Works on any device, No learning curve

- **Testimonials Section**: 3 placeholder testimonials with 5-star ratings
  - Social proof from UK hosts in Manchester, London, Bristol

- **Pricing Section**: Improved toggle and card design
  - "2 months free" badge on annual toggle
  - Plan highlights above each card
  - Clearer savings messaging

- **FAQ Section**: 8 comprehensive questions
  - Covers documents tracked, reminders, uploads, security, UK nations, trial, setup, cancellation

- **Final CTA Section**: Dark background with urgency
  - "Ready to stop worrying about compliance?"
  - Dual CTA buttons

### Document Preview Feature (March 27, 2026)
- **Document Display on Compliance Cards**:
  - Paperclip icon with document count badge (📎 1)
  - Document thumbnails showing filename with file type icon
  - Eye icon on hover for preview action
  - Support for showing up to 3 documents + "more" indicator

- **Document Preview Modal (DocumentPreviewModal.js)**:
  - Full-size image preview with dark background
  - Zoom controls (25% increments, 50% to 300%)
  - Rotate button (90° clockwise)
  - Download button
  - PDF support via iframe
  - Navigation arrows for multiple documents
  - Accessible with DialogTitle for screen readers

### Phase 5 Stripe Integration Stabilization (March 27, 2026)
- Fixed BillingSuccessPage polling loop - now correctly passes attempt count
- Fixed 404 handling - immediately shows error for invalid payment sessions instead of waiting for timeout
- Verified all backend APIs working: auth, properties, compliance, tasks, dashboard, subscription, payments
- Verified all frontend flows: signup, login, CRUD operations, form validation, mobile layout
- All 51 backend tests + full frontend UI tests passed (100%)

## Recent Implementations

### Stripe Payment Integration (March 27, 2026)
- **Stripe Checkout Integration**:
  - Created checkout session API `/api/payments/checkout`
  - Secure Stripe redirect for subscription payments
  - Support for monthly and annual billing cycles
  - Payment transactions collection for tracking

- **Payment Status Polling**:
  - Status check API `/api/payments/status/{session_id}`
  - Frontend polling on success page
  - Automatic subscription activation on payment success

- **Webhook Support**:
  - Stripe webhook handler `/api/webhook/stripe`
  - Payment status updates via webhooks

- **UI Updates**:
  - BillingPage shows "Subscribe" button for trial users
  - Payment Method section shows "Secure Stripe Checkout"
  - BillingSuccessPage with payment verification polling
  - Redirects to Stripe checkout on subscription click

### Audit-Ready Export & Polish (December 2025)
- **PDF Compliance Reports**:
  - `/api/properties/{id}/export` endpoint generates PDF using ReportLab
  - Property details, compliance summary, records table, tasks, documents
  - Color-coded status (compliant=green, expiring_soon=amber, overdue=red)
  - Company name branding support via user preferences
  - Download via "Export Report" button on property detail page

- **Enhanced Settings Page**:
  - Complete rewrite with 4 tabbed sections:
  - Account Tab: User info (read-only), Company Name (editable)
  - Notifications Tab: In-app/Email/Weekly digest/Marketing toggles, Reminder timing selection
  - Security Tab: Password change form with validation (8+ chars, match check)
  - Support Tab: Contact form with type selector (Support/Billing/Feedback)

- **Help Center Page**:
  - Getting Started: 4-step onboarding guide
  - FAQ: 4 categories with expandable accordion
  - Contact Support CTA linking to Settings

### AI Assistant (December 2025)
- **Dashboard Compliance Assistant**:
  - Dark-themed panel on dashboard left side
  - Priority summary cards:
    - Highest Risk Property (with risk reasons)
    - Next Urgent Actions (critical/high priority items)
    - Missing Records by property
  - Quick Questions: Pre-built suggested queries
  - Natural language input with Send button
  - GPT-4o powered responses grounded in user data

- **Property-Level Assistant**:
  - AI Summary panel on each property detail page
  - Compliance Score (0-100%) with color-coded badge
  - Quick stats: Compliant/Expiring/Overdue/Missing
  - Recommended Actions: Clickable cards with priority levels
  - Pending Tasks: Upcoming task list with due dates

- **API Endpoints**:
  - GET `/api/assistant/insights` - Structured dashboard insights
  - GET `/api/assistant/property/{id}` - Property-level insights
  - POST `/api/assistant/ask` - Natural language queries

- **Technical Implementation**:
  - `ai_assistant.py`: Pure data queries for structured insights (fast, accurate)
  - GPT-4o via emergentintegrations for natural language (grounded responses)
  - Risk scoring algorithm: Overdue (30pts), Missing (20pts), Expiring (10pts)

### Stabilization Phase (December 2025)
- **Plan Limit Enforcement**: 
  - Solo=1, Portfolio=5, Operator=15 properties
  - 403 error with upgrade message when limit reached
  - PropertyModal shows upgrade prompt with pricing

- **Sidebar Plan Display**:
  - Shows actual plan name (Solo/Portfolio/Operator) with (Trial) suffix
  - Replaced hardcoded "Free Trial" with dynamic user context

- **Data Consistency**:
  - Dashboard stats match actual database counts
  - Status badges update correctly based on expiry dates

- **Form Validation**:
  - Backend validates all required fields
  - Clear error messages returned to frontend

- **Mobile/Responsive**:
  - Sidebar hidden by default on mobile
  - Hamburger menu opens sidebar
  - Compliance table horizontally scrollable

- **Demo Mode Polish**:
  - Creates Portfolio trial with 3 UK properties
  - 12 compliance records with varied statuses
  - 6 sample tasks
  - Onboarding marked as completed

### Refactoring Complete (December 2025)
- **Code Modularization** - server.py reduced from 2100+ to 870 lines:
  - `/routes/auth.py` - Authentication (signup, login, demo, password reset)
  - `/routes/properties.py` - Property CRUD + PDF export
  - `/routes/compliance.py` - Compliance records CRUD + documents
  - `/routes/tasks.py` - Tasks CRUD + templates
  - `/routes/notifications.py` - Notifications + user preferences
  - `/routes/billing.py` - Subscription + Stripe checkout
  - `/models/database.py` - MongoDB connection
  - `/models/schemas.py` - Pydantic models
  - `/utils/auth.py` - JWT, password utilities
  - `/utils/constants.py` - Plans, categories
  - `/utils/email_service.py` - Resend email templates

- **Email Service (Resend)**:
  - Professional HTML templates ready
  - Graceful fallback when RESEND_API_KEY not set

## Next Tasks (P1)
1. Configure RESEND_API_KEY in production for real email sending
2. Set up weekly email digest scheduler

## Future Tasks (P2)
1. Team access / multi-user support
2. Social login (Google Auth)
3. Mobile app / PWA
4. API access for Operator tier

## Mocked Functionality
- **Email Notifications**: Works when RESEND_API_KEY is configured. UI toggle exists with "Coming soon" badge, preference saved. Email templates ready.
- **Weekly Digest**: Toggle exists with "Coming soon" badge, template available
- **Contact Form**: Saves to database, email notification ready when configured

## Key API Endpoints

### Documents
- POST `/api/documents/upload` - Upload file (optional compliance_record_id to link)
- POST `/api/documents/upload-and-extract` - Upload + AI extraction
- GET `/api/documents/{id}` - Get document metadata
- GET `/api/documents/{id}/download` - Download file
- PUT `/api/documents/{id}/link` - Link document to compliance record
- DELETE `/api/documents/{id}` - Delete document
- GET `/api/compliance-records/{record_id}/documents` - Get record's documents

### New Endpoints (December 2025)
- GET `/api/properties/{id}/export` - Generate PDF compliance report
- POST `/api/auth/change-password` - Change user's password
- POST `/api/contact` - Submit support/billing/feedback request

### AI Assistant Endpoints
- GET `/api/assistant/insights` - Dashboard structured insights
- GET `/api/assistant/property/{id}` - Property-level insights
- POST `/api/assistant/ask` - Natural language queries (GPT-4o)

### Other Endpoints (Previous Phases)
- Auth: `/api/auth/signup`, `/api/auth/login`, `/api/auth/forgot-password`, `/api/auth/demo`
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
