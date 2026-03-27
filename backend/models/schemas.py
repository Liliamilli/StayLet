"""
Pydantic schemas for Staylet API.
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional


# Payment Models
class CheckoutRequest(BaseModel):
    plan: str  # solo, portfolio, operator
    billing_cycle: str = "monthly"  # monthly or annual
    origin_url: str  # Frontend origin URL for success/cancel redirects


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class PaymentStatusResponse(BaseModel):
    status: str
    payment_status: str
    plan: Optional[str] = None
    billing_cycle: Optional[str] = None
    success: bool = False
    message: str = ""


# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    full_name: str
    created_at: str
    subscription_plan: str = "solo"
    subscription_status: str = "trial"
    trial_start: Optional[str] = None
    trial_end: Optional[str] = None
    property_limit: int = 1
    property_count: int = 0


class AuthResponse(BaseModel):
    user: UserResponse
    token: str


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    plan: str
    plan_name: str
    status: str
    property_limit: int
    property_count: int
    trial_start: Optional[str] = None
    trial_end: Optional[str] = None
    trial_days_remaining: Optional[int] = None
    price_monthly: int
    price_yearly: int
    features: List[str]
    can_upgrade: bool
    can_downgrade: bool


class SubscriptionUpdate(BaseModel):
    plan: str  # solo, portfolio, operator


class PlanLimitCheck(BaseModel):
    allowed: bool
    current_count: int
    limit: int
    plan: str
    message: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetResponse(BaseModel):
    message: str
    success: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# Property Models
class PropertyCreate(BaseModel):
    name: str
    address: str
    postcode: str
    uk_nation: str = "England"
    is_in_london: bool = False
    property_type: str = "apartment"
    ownership_type: str = "owned"
    bedrooms: int = 1
    notes: Optional[str] = None


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    uk_nation: Optional[str] = None
    is_in_london: Optional[bool] = None
    property_type: Optional[str] = None
    ownership_type: Optional[str] = None
    bedrooms: Optional[int] = None
    notes: Optional[str] = None
    property_status: Optional[str] = None


class PropertyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    name: str
    address: str
    postcode: str
    uk_nation: str
    is_in_london: bool
    property_type: str
    ownership_type: str
    bedrooms: int
    notes: Optional[str] = None
    property_status: str
    compliance_summary: Optional[dict] = None
    created_at: str
    updated_at: str


# Compliance Models
class ComplianceRecordCreate(BaseModel):
    property_id: str
    title: str
    category: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    reminder_preference: str = "30_days"
    notes: Optional[str] = None


class ComplianceRecordUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    reminder_preference: Optional[str] = None
    notes: Optional[str] = None
    compliance_status: Optional[str] = None


class ComplianceRecordResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    property_id: str
    title: str
    category: str
    compliance_status: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    reminder_preference: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class BulkComplianceCreate(BaseModel):
    property_id: str
    records: List[dict]


# Task Models
class TaskCreate(BaseModel):
    property_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"
    category: str = "general"
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly, yearly


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    task_status: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    property_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str
    task_status: str
    category: str
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    created_at: str
    updated_at: str


# Notification Models
class NotificationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    notification_type: str
    title: str
    message: str
    reference_type: Optional[str] = None  # property, compliance_record, task
    reference_id: Optional[str] = None
    is_read: bool = False
    created_at: str


# User Preferences Models
class UserPreferencesUpdate(BaseModel):
    email_reminders: Optional[bool] = None
    inapp_reminders: Optional[bool] = None
    reminder_lead_days: Optional[List[int]] = None
    company_name: Optional[str] = None
    weekly_digest: Optional[bool] = None
    marketing_emails: Optional[bool] = None


class UserPreferencesResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    email_reminders: bool = True
    inapp_reminders: bool = True
    reminder_lead_days: List[int] = [90, 60, 30, 7]
    company_name: Optional[str] = None
    weekly_digest: bool = True
    marketing_emails: bool = False


# Contact Form
class ContactFormRequest(BaseModel):
    subject: str
    message: str
    contact_type: str = "support"  # support, billing, feedback


# Document Models
class DocumentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    compliance_record_id: Optional[str] = None
    user_id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    uploaded_at: str


class ExtractionSuggestion(BaseModel):
    value: Optional[str] = None
    label: Optional[str] = None
    raw_text: Optional[str] = None
    confidence: str = "LOW"
    is_suggested: bool = True


class ExtractionResult(BaseModel):
    success: bool
    error: Optional[str] = None
    suggestions: Optional[dict] = None


# Dashboard Models
class DashboardStats(BaseModel):
    total_properties: int = 0
    upcoming_expiries: int = 0
    overdue_items: int = 0
    missing_records: int = 0
    tasks_due: int = 0
    tasks_due_this_month: int = 0
    unread_notifications: int = 0


class UpcomingExpiry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    category: str
    property_id: str
    property_name: str
    expiry_date: str
    days_until_expiry: int
    compliance_status: str


class DashboardData(BaseModel):
    stats: DashboardStats
    upcoming_expiries: List[UpcomingExpiry] = []
    overdue_records: List[dict] = []
    tasks_due_this_month: List[dict] = []


# AI Assistant Models
class AssistantQueryRequest(BaseModel):
    question: str


# Onboarding Models
class OnboardingStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")
    steps_completed: List[str] = []
    is_complete: bool = False
    current_step: int = 1
