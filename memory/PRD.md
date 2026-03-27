# Staylet - Product Requirements Document

## Original Problem Statement
Build the foundation of a SaaS web app called Staylet that helps UK short-term let hosts track compliance records, expiry dates, required documents, and property admin. Phase 1 focuses on the core app shell and authentication only.

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
4. Dashboard with 5 stat cards (properties, expiries, overdue, missing docs, tasks)
5. Placeholder pages: Properties, Compliance, Tasks, Billing, Settings
6. MongoDB data models for users, subscriptions, properties, compliance_records, tasks, notifications, uploaded_files

## What's Been Implemented (Phase 1 Complete - March 27, 2026)

### Backend
- FastAPI server with JWT authentication
- bcrypt password hashing
- MongoDB async driver (Motor)
- Complete data models for all entities
- Auth endpoints: signup, login, me, reset-password (mocked)
- Dashboard stats endpoint
- Properties CRUD endpoints
- Tasks CRUD endpoints
- Notifications endpoint

### Frontend
- React app with React Router
- AuthContext for state management
- ProtectedRoute component
- Landing page with hero, benefits, pricing, FAQ sections
- Login, Signup, Reset Password pages
- App shell with sidebar and header
- Dashboard with 5 stat cards
- Empty states for all placeholder pages
- Responsive design (desktop-first)

### Design System
- Outfit font for headings, Inter for body
- Blue primary color (#2563EB)
- Status colors: emerald (success), amber (warning), red (error)
- Clean white backgrounds with subtle borders
- Shadcn UI components

## Prioritized Backlog

### P0 (Phase 2 - Next)
- Add Property form and CRUD UI
- Property detail page
- Compliance document upload/tracking
- Expiry date tracking with status indicators

### P1 (Phase 3)
- Tasks CRUD UI
- Email notifications (integrate with SendGrid/Resend)
- Document storage integration
- Reminder system for expiring documents

### P2 (Future)
- Social login (Google)
- Stripe billing integration
- Team access/multi-user
- Mobile app or PWA
- API access for Business tier
- Export/reports

## Next Tasks
1. Build Add Property modal/form
2. Create Property detail page with compliance tracking
3. Implement document upload functionality
4. Add real email sending for password reset
5. Build Tasks management UI
