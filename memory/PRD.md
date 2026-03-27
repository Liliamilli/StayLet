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
7. MongoDB data models for all entities

## What's Been Implemented

### Phase 1 (March 27, 2026) - Foundation
- Landing page with hero, benefits, pricing, FAQ
- JWT authentication (signup, login, logout, reset mocked)
- App shell with sidebar navigation
- Dashboard with placeholder stats
- Empty state pages for all sections

### Phase 2 (March 27, 2026) - Compliance Tracking
- **Properties CRUD**:
  - Create/Edit/Delete properties
  - Fields: name, address, postcode, UK nation, is_in_london, property_type, ownership_type, bedrooms, notes
  - Search functionality
  - Property cards with compliance summary

- **Property Detail Page**:
  - Property info display
  - Compliance summary (total, compliant, expiring_soon, overdue, missing)
  - Compliance records list
  - Tasks section (placeholder)

- **Compliance Records CRUD**:
  - Categories: gas_safety, eicr, epc, insurance, fire_risk_assessment, pat_testing, legionella, smoke_co_alarms, licence, custom
  - Fields: title, category, issue_date, expiry_date, reminder_preference, notes
  - Auto-fill title from category
  - Auto-calculate status based on expiry date

- **Status Logic**:
  - compliant: no expiry or expiry > 30 days
  - expiring_soon: expiry within 30 days
  - overdue: expiry date passed
  - missing: no document uploaded

- **Dashboard with Real Data**:
  - Total properties count
  - Upcoming expiries (within 30 days)
  - Overdue items
  - Missing records
  - Tasks due
  - Compliance alerts panel

- **Compliance Page**:
  - List all records across properties
  - Filter by status and category
  - Sort by priority (overdue first)
  - Click to navigate to property

## Tech Stack
- React + Tailwind + Shadcn UI
- FastAPI + MongoDB (Motor async driver)
- JWT auth with bcrypt password hashing
- Outfit/Inter fonts, Blue (#2563EB) primary

## Prioritized Backlog

### P0 (Next)
- Task management CRUD
- Email notifications for expiring documents
- Document file upload and storage

### P1 (Future)
- Real email sending for password reset
- Stripe billing integration
- Team access/multi-user

### P2 (Later)
- Social login (Google)
- Mobile app or PWA
- API access for Business tier
- Export/reports

## Next Tasks
1. Build Tasks management UI with CRUD
2. Integrate document upload (object storage)
3. Add email notifications via SendGrid/Resend
4. Implement Stripe billing integration
