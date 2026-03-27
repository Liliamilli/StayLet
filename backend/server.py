from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import base64
import aiofiles
from document_extraction import extract_document_info, format_extracted_for_ui, suggest_category_from_filename
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from pdf_generator import generate_compliance_report
from ai_assistant import get_structured_insights, get_property_insights, answer_natural_language_query

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# File upload configuration
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg"
}

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'staylet-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

app = FastAPI(title="Staylet API", version="1.0.0")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
UK_NATIONS = ["England", "Scotland", "Wales", "Northern Ireland"]
PROPERTY_TYPES = ["apartment", "house", "studio", "maisonette", "bungalow", "townhouse", "detached", "semi-detached", "terraced", "other"]
OWNERSHIP_TYPES = ["owned", "leased", "managed_for_owner", "rent_to_rent", "other"]
COMPLIANCE_CATEGORIES = ["gas_safety", "eicr", "epc", "insurance", "fire_risk_assessment", "pat_testing", "legionella", "smoke_co_alarms", "licence", "custom"]
COMPLIANCE_STATUS = ["compliant", "expiring_soon", "overdue", "missing"]
REMINDER_OPTIONS = ["none", "30_days", "60_days", "90_days"]
TASK_STATUSES = ["pending", "in_progress", "completed"]
TASK_PRIORITIES = ["low", "medium", "high", "urgent"]
TASK_CATEGORIES = ["general", "maintenance", "inspection", "renewal", "safety", "seasonal", "admin"]
NOTIFICATION_TYPES = ["expiry_reminder", "overdue_alert", "task_due", "missing_record", "system"]
REMINDER_INTERVALS = [90, 60, 30, 7, 0]  # Days before expiry (0 = overdue)

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "solo": {
        "name": "Solo",
        "price_monthly": 19,
        "price_yearly": 190,
        "property_limit": 1,
        "features": ["1 property", "Compliance tracking", "Document storage", "Email reminders", "Task management"]
    },
    "portfolio": {
        "name": "Portfolio",
        "price_monthly": 39,
        "price_yearly": 390,
        "property_limit": 5,
        "features": ["Up to 5 properties", "Everything in Solo", "Priority support", "Bulk compliance setup", "Advanced reports"]
    },
    "operator": {
        "name": "Operator",
        "price_monthly": 79,
        "price_yearly": 790,
        "property_limit": 15,
        "features": ["Up to 15 properties", "Everything in Portfolio", "API access", "Team members (coming soon)", "Custom integrations"]
    }
}
SUBSCRIPTION_STATUSES = ["trial", "active", "past_due", "cancelled", "expired"]
TRIAL_DAYS = 14

# Stripe Configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

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

# Models
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

class ContactFormRequest(BaseModel):
    subject: str
    message: str
    contact_type: str = "support"  # support, billing, feedback

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

# Auth helpers
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str) -> str:
    payload = {"user_id": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS), "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = decode_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def calculate_compliance_status(expiry_date: Optional[str], has_document: bool = True) -> str:
    if not has_document:
        return "missing"
    if not expiry_date:
        return "compliant"
    try:
        expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        days_until_expiry = (expiry - datetime.now(timezone.utc)).days
        if days_until_expiry < 0:
            return "overdue"
        elif days_until_expiry <= 30:
            return "expiring_soon"
        return "compliant"
    except (ValueError, TypeError):
        return "compliant"

async def get_property_compliance_summary(property_id: str, user_id: str) -> dict:
    records = await db.compliance_records.find({"property_id": property_id, "user_id": user_id}, {"_id": 0}).to_list(100)
    summary = {"total": len(records), "compliant": 0, "expiring_soon": 0, "overdue": 0, "missing": 0}
    for record in records:
        status = record.get("compliance_status", "compliant")
        if status in summary:
            summary[status] += 1
    return summary

# Auth Routes
@api_router.post("/auth/signup", response_model=AuthResponse)
async def signup(user_data: UserCreate):
    if await db.users.find_one({"email": user_data.email.lower()}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=TRIAL_DAYS)
    user_doc = {
        "id": user_id, 
        "email": user_data.email.lower(), 
        "password": hash_password(user_data.password), 
        "full_name": user_data.full_name, 
        "subscription_plan": "solo",
        "subscription_status": "trial",
        "trial_start": now.isoformat(),
        "trial_end": trial_end.isoformat(),
        "created_at": now.isoformat(), 
        "updated_at": now.isoformat()
    }
    await db.users.insert_one(user_doc)
    token = create_token(user_id, user_data.email.lower())
    property_count = 0
    plan_info = SUBSCRIPTION_PLANS.get("solo", {})
    return AuthResponse(
        user=UserResponse(
            id=user_id, 
            email=user_data.email.lower(), 
            full_name=user_data.full_name, 
            created_at=now.isoformat(),
            subscription_plan="solo",
            subscription_status="trial",
            trial_start=now.isoformat(),
            trial_end=trial_end.isoformat(),
            property_limit=plan_info.get("property_limit", 1),
            property_count=property_count
        ), 
        token=token
    )

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email.lower()}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check and update trial status if expired
    subscription_status = user.get("subscription_status", "trial")
    if subscription_status == "trial" and user.get("trial_end"):
        trial_end = datetime.fromisoformat(user["trial_end"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > trial_end:
            subscription_status = "expired"
            await db.users.update_one({"id": user["id"]}, {"$set": {"subscription_status": "expired"}})
    
    token = create_token(user["id"], user["email"])
    property_count = await db.properties.count_documents({"user_id": user["id"], "property_status": "active"})
    plan = user.get("subscription_plan", "solo")
    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["solo"])
    
    return AuthResponse(
        user=UserResponse(
            id=user["id"], 
            email=user["email"], 
            full_name=user["full_name"], 
            created_at=user["created_at"],
            subscription_plan=plan,
            subscription_status=subscription_status,
            trial_start=user.get("trial_start"),
            trial_end=user.get("trial_end"),
            property_limit=plan_info.get("property_limit", 1),
            property_count=property_count
        ), 
        token=token
    )

@api_router.post("/auth/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: PasswordResetRequest):
    _ = await db.users.find_one({"email": request.email.lower()})
    return PasswordResetResponse(message="If an account exists with this email, you will receive password reset instructions.", success=True)

# Change Password
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@api_router.post("/auth/change-password")
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    """Change user's password."""
    # Fetch user with password for verification (get_current_user excludes password)
    user_with_password = await db.users.find_one({"id": current_user["id"]}, {"_id": 0})
    if not user_with_password:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Verify current password
    if not verify_password(request.current_password, user_with_password["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Hash new password and update
    new_hashed = hash_password(request.new_password)
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"password": new_hashed, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"success": True, "message": "Password changed successfully"}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    # Check and update trial status if expired
    subscription_status = current_user.get("subscription_status", "trial")
    if subscription_status == "trial" and current_user.get("trial_end"):
        trial_end = datetime.fromisoformat(current_user["trial_end"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > trial_end:
            subscription_status = "expired"
            await db.users.update_one({"id": current_user["id"]}, {"$set": {"subscription_status": "expired"}})
    
    property_count = await db.properties.count_documents({"user_id": current_user["id"], "property_status": "active"})
    plan = current_user.get("subscription_plan", "solo")
    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["solo"])
    
    return UserResponse(
        id=current_user["id"], 
        email=current_user["email"], 
        full_name=current_user["full_name"], 
        created_at=current_user["created_at"],
        subscription_plan=plan,
        subscription_status=subscription_status,
        trial_start=current_user.get("trial_start"),
        trial_end=current_user.get("trial_end"),
        property_limit=plan_info.get("property_limit", 1),
        property_count=property_count
    )

# Demo Mode - Create demo account with seed data
@api_router.post("/auth/demo", response_model=AuthResponse)
async def create_demo_account():
    """Create a demo account with realistic sample data for UK short-let properties."""
    import random
    
    # Generate unique demo user
    demo_id = str(uuid.uuid4())
    demo_email = f"demo_{demo_id[:8]}@staylet-demo.com"
    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=TRIAL_DAYS)
    
    # Create demo user with Portfolio plan for full features
    user_doc = {
        "id": demo_id,
        "email": demo_email,
        "password": hash_password("demo123"),
        "full_name": "Demo User",
        "subscription_plan": "portfolio",
        "subscription_status": "trial",
        "trial_start": now.isoformat(),
        "trial_end": trial_end.isoformat(),
        "is_demo": True,
        "onboarding_completed": True,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    await db.users.insert_one(user_doc)
    
    # Create 3 realistic UK properties
    properties_data = [
        {
            "name": "Victoria Terrace Apartment",
            "address": "42 Victoria Terrace",
            "postcode": "SW1V 1AA",
            "uk_nation": "England",
            "is_in_london": True,
            "property_type": "apartment",
            "ownership_type": "owned",
            "bedrooms": 2
        },
        {
            "name": "Cotswold Cottage",
            "address": "Rose Cottage, High Street",
            "postcode": "GL54 2HN",
            "uk_nation": "England",
            "is_in_london": False,
            "property_type": "house",
            "ownership_type": "owned",
            "bedrooms": 3
        },
        {
            "name": "Edinburgh Old Town Flat",
            "address": "15 Royal Mile Close",
            "postcode": "EH1 1QS",
            "uk_nation": "Scotland",
            "is_in_london": False,
            "property_type": "apartment",
            "ownership_type": "owned",
            "bedrooms": 1
        }
    ]
    
    property_ids = []
    for prop_data in properties_data:
        prop_id = str(uuid.uuid4())
        property_ids.append(prop_id)
        prop_doc = {
            "id": prop_id,
            "user_id": demo_id,
            **prop_data,
            "property_status": "active",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        await db.properties.insert_one(prop_doc)
    
    # Create compliance records with varied statuses
    compliance_data = [
        # Property 1 - Victoria Terrace (mixed status)
        {"property_id": property_ids[0], "title": "Gas Safety Certificate", "category": "gas_safety", 
         "expiry_date": (now + timedelta(days=45)).date().isoformat(), "status": "expiring_soon",
         "notes": "Annual inspection by British Gas engineer"},
        {"property_id": property_ids[0], "title": "EICR Certificate", "category": "eicr", 
         "expiry_date": (now + timedelta(days=400)).date().isoformat(), "status": "compliant",
         "notes": "5-year electrical inspection completed"},
        {"property_id": property_ids[0], "title": "EPC Rating", "category": "epc", 
         "expiry_date": (now + timedelta(days=1200)).date().isoformat(), "status": "compliant",
         "notes": "Rating: C (72)"},
        {"property_id": property_ids[0], "title": "Landlord Insurance", "category": "insurance", 
         "expiry_date": (now - timedelta(days=5)).date().isoformat(), "status": "overdue",
         "notes": "Buildings and contents with Aviva - RENEWAL NEEDED"},
        
        # Property 2 - Cotswold Cottage (mostly compliant)
        {"property_id": property_ids[1], "title": "Gas Safety Certificate", "category": "gas_safety", 
         "expiry_date": (now + timedelta(days=200)).date().isoformat(), "status": "compliant",
         "notes": "Local Gas Safe engineer - expires August"},
        {"property_id": property_ids[1], "title": "EICR Certificate", "category": "eicr", 
         "expiry_date": (now + timedelta(days=25)).date().isoformat(), "status": "expiring_soon",
         "notes": "Due for renewal next month"},
        {"property_id": property_ids[1], "title": "Fire Risk Assessment", "category": "fire_risk_assessment", 
         "expiry_date": (now + timedelta(days=90)).date().isoformat(), "status": "compliant",
         "notes": "Smoke alarms and fire extinguisher checked"},
        {"property_id": property_ids[1], "title": "EPC Rating", "category": "epc", 
         "expiry_date": (now + timedelta(days=2500)).date().isoformat(), "status": "compliant",
         "notes": "Rating: B (85) - recently upgraded insulation"},
        
        # Property 3 - Edinburgh (Scotland-specific)
        {"property_id": property_ids[2], "title": "Gas Safety Certificate", "category": "gas_safety", 
         "expiry_date": (now + timedelta(days=15)).date().isoformat(), "status": "expiring_soon",
         "notes": "Booked with Scottish Gas for next week"},
        {"property_id": property_ids[2], "title": "Short-Term Let Licence", "category": "licence", 
         "expiry_date": (now + timedelta(days=300)).date().isoformat(), "status": "compliant",
         "notes": "Edinburgh Council licence - 3 year term"},
        {"property_id": property_ids[2], "title": "EICR Certificate", "category": "eicr", 
         "expiry_date": (now - timedelta(days=30)).date().isoformat(), "status": "overdue",
         "notes": "URGENT: Electrical inspection overdue"},
        {"property_id": property_ids[2], "title": "Legionella Risk Assessment", "category": "legionella", 
         "expiry_date": (now + timedelta(days=180)).date().isoformat(), "status": "compliant",
         "notes": "Water system checked - low risk"}
    ]
    
    for comp_data in compliance_data:
        comp_id = str(uuid.uuid4())
        expiry = datetime.fromisoformat(comp_data["expiry_date"])
        days_until = (expiry.date() - now.date()).days
        
        if days_until < 0:
            calc_status = "overdue"
        elif days_until <= 30:
            calc_status = "expiring_soon"
        else:
            calc_status = "compliant"
        
        comp_doc = {
            "id": comp_id,
            "user_id": demo_id,
            "property_id": comp_data["property_id"],
            "title": comp_data["title"],
            "category": comp_data["category"],
            "expiry_date": comp_data["expiry_date"],
            "compliance_status": calc_status,
            "notes": comp_data.get("notes", ""),
            "reminder_preference": "30_days",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        await db.compliance_records.insert_one(comp_doc)
    
    # Create tasks with varied priorities and due dates
    tasks_data = [
        {"property_id": property_ids[0], "title": "Renew landlord insurance", 
         "description": "Get quotes from Aviva, Direct Line, and Hiscox", 
         "due_date": (now + timedelta(days=2)).date().isoformat(), "priority": "high", "task_status": "pending", "category": "renewal"},
        {"property_id": property_ids[0], "title": "Replace smoke alarm batteries", 
         "description": "Check all units before next guest arrival", 
         "due_date": (now + timedelta(days=7)).date().isoformat(), "priority": "medium", "task_status": "pending", "category": "safety"},
        {"property_id": property_ids[1], "title": "Book EICR inspection", 
         "description": "Contact local electrician for 5-year check", 
         "due_date": (now + timedelta(days=5)).date().isoformat(), "priority": "high", "task_status": "pending", "category": "inspection"},
        {"property_id": property_ids[1], "title": "Schedule boiler service", 
         "description": "Annual service - check heating efficiency", 
         "due_date": (now + timedelta(days=14)).date().isoformat(), "priority": "medium", "task_status": "pending", "category": "maintenance"},
        {"property_id": property_ids[2], "title": "Urgent: Book EICR inspection", 
         "description": "Certificate expired - arrange immediately", 
         "due_date": now.date().isoformat(), "priority": "high", "task_status": "pending", "category": "inspection"},
        {"property_id": property_ids[2], "title": "Confirm gas safety appointment", 
         "description": "Scottish Gas visit scheduled for next week", 
         "due_date": (now + timedelta(days=3)).date().isoformat(), "priority": "medium", "task_status": "in_progress", "category": "inspection"}
    ]
    
    for task_data in tasks_data:
        task_id = str(uuid.uuid4())
        task_doc = {
            "id": task_id,
            "user_id": demo_id,
            **task_data,
            "is_recurring": False,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        await db.tasks.insert_one(task_doc)
    
    # Update property compliance summaries
    for prop_id in property_ids:
        records = await db.compliance_records.find({"property_id": prop_id}).to_list(100)
        summary = {"total": 0, "compliant": 0, "expiring_soon": 0, "overdue": 0, "missing": 0}
        for record in records:
            summary["total"] += 1
            status = record.get("compliance_status", "compliant")
            if status in summary:
                summary[status] += 1
        await db.properties.update_one({"id": prop_id}, {"$set": {"compliance_summary": summary}})
    
    # Create auth token
    token = create_token(demo_id, demo_email)
    plan_info = SUBSCRIPTION_PLANS.get("portfolio", {})
    
    return AuthResponse(
        user=UserResponse(
            id=demo_id,
            email=demo_email,
            full_name="Demo User",
            created_at=now.isoformat(),
            subscription_plan="portfolio",
            subscription_status="trial",
            trial_start=now.isoformat(),
            trial_end=trial_end.isoformat(),
            property_limit=plan_info.get("property_limit", 5),
            property_count=3
        ),
        token=token
    )

# User Onboarding Status
class OnboardingStatus(BaseModel):
    completed: bool
    current_step: int
    steps_completed: List[str]

@api_router.get("/user/onboarding", response_model=OnboardingStatus)
async def get_onboarding_status(current_user: dict = Depends(get_current_user)):
    """Get user's onboarding progress."""
    user_id = current_user["id"]
    
    # Check what the user has done
    has_property = await db.properties.count_documents({"user_id": user_id, "property_status": "active"}) > 0
    has_compliance = await db.compliance_records.count_documents({"user_id": user_id}) > 0
    has_viewed_dashboard = current_user.get("has_viewed_dashboard", False)
    
    steps_completed = []
    if has_property:
        steps_completed.append("add_property")
    if has_compliance:
        steps_completed.append("add_compliance")
    if has_viewed_dashboard:
        steps_completed.append("view_dashboard")
    
    # Determine current step
    current_step = 0
    if not has_property:
        current_step = 1
    elif not has_compliance:
        current_step = 2
    elif not has_viewed_dashboard:
        current_step = 3
    else:
        current_step = 4  # Complete
    
    completed = current_user.get("onboarding_completed", False) or len(steps_completed) >= 3
    
    return OnboardingStatus(
        completed=completed,
        current_step=current_step,
        steps_completed=steps_completed
    )

@api_router.post("/user/onboarding/complete")
async def complete_onboarding(current_user: dict = Depends(get_current_user)):
    """Mark onboarding as complete."""
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"onboarding_completed": True, "has_viewed_dashboard": True}}
    )
    return {"success": True}

# Dashboard Routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    total_properties = await db.properties.count_documents({"user_id": user_id, "property_status": "active"})
    compliance_records = await db.compliance_records.find({"user_id": user_id}, {"_id": 0, "compliance_status": 1}).to_list(1000)
    upcoming_expiries = sum(1 for r in compliance_records if r.get("compliance_status") == "expiring_soon")
    overdue_items = sum(1 for r in compliance_records if r.get("compliance_status") == "overdue")
    missing_records = sum(1 for r in compliance_records if r.get("compliance_status") == "missing")
    tasks_due = await db.tasks.count_documents({"user_id": user_id, "task_status": {"$in": ["pending", "in_progress"]}})
    
    # Calculate tasks due this month
    now = datetime.now(timezone.utc)
    month_end = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    tasks_this_month = await db.tasks.count_documents({
        "user_id": user_id, 
        "task_status": {"$in": ["pending", "in_progress"]},
        "due_date": {"$lte": month_end.isoformat(), "$gte": now.isoformat()}
    })
    
    unread_notifications = await db.notifications.count_documents({"user_id": user_id, "is_read": False})
    
    return DashboardStats(
        total_properties=total_properties, 
        upcoming_expiries=upcoming_expiries, 
        overdue_items=overdue_items, 
        missing_records=missing_records, 
        tasks_due=tasks_due,
        tasks_due_this_month=tasks_this_month,
        unread_notifications=unread_notifications
    )

@api_router.get("/dashboard/data", response_model=DashboardData)
async def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Get comprehensive dashboard data including upcoming expiries, overdue items, and tasks"""
    user_id = current_user["id"]
    now = datetime.now(timezone.utc)
    
    # Get stats
    stats = await get_dashboard_stats(current_user)
    
    # Get properties for name lookup
    properties = await db.properties.find({"user_id": user_id}, {"_id": 0, "id": 1, "name": 1}).to_list(100)
    prop_map = {p["id"]: p["name"] for p in properties}
    
    # Get upcoming expiries (next 5, sorted by expiry date)
    upcoming_records = await db.compliance_records.find(
        {"user_id": user_id, "compliance_status": {"$in": ["expiring_soon", "compliant"]}, "expiry_date": {"$ne": None}},
        {"_id": 0}
    ).to_list(100)
    
    upcoming_expiries = []
    for record in upcoming_records:
        try:
            expiry = datetime.fromisoformat(record["expiry_date"].replace('Z', '+00:00'))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            days_until = (expiry - now).days
            if days_until >= 0 and days_until <= 90:
                upcoming_expiries.append({
                    "id": record["id"],
                    "title": record["title"],
                    "category": record["category"],
                    "property_id": record["property_id"],
                    "property_name": prop_map.get(record["property_id"], "Unknown"),
                    "expiry_date": record["expiry_date"],
                    "days_until_expiry": days_until,
                    "compliance_status": record["compliance_status"]
                })
        except (ValueError, TypeError):
            continue
    
    upcoming_expiries.sort(key=lambda x: x["days_until_expiry"])
    upcoming_expiries = upcoming_expiries[:5]
    
    # Get overdue records
    overdue_records = await db.compliance_records.find(
        {"user_id": user_id, "compliance_status": "overdue"},
        {"_id": 0}
    ).to_list(20)
    
    for record in overdue_records:
        record["property_name"] = prop_map.get(record["property_id"], "Unknown")
    
    # Get tasks due this month
    month_end = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    tasks_this_month = await db.tasks.find(
        {"user_id": user_id, "task_status": {"$in": ["pending", "in_progress"]}},
        {"_id": 0}
    ).sort("due_date", 1).to_list(100)
    
    # Filter tasks with due dates this month or overdue
    filtered_tasks = []
    for task in tasks_this_month:
        if task.get("due_date"):
            try:
                due = datetime.fromisoformat(task["due_date"].replace('Z', '+00:00'))
                if due.tzinfo is None:
                    due = due.replace(tzinfo=timezone.utc)
                if due <= month_end:
                    task["property_name"] = prop_map.get(task.get("property_id"), None)
                    task["is_overdue"] = due < now
                    filtered_tasks.append(task)
            except (ValueError, TypeError):
                continue
        else:
            # Include tasks without due date
            task["property_name"] = prop_map.get(task.get("property_id"), None)
            task["is_overdue"] = False
            filtered_tasks.append(task)
    
    return DashboardData(
        stats=stats,
        upcoming_expiries=upcoming_expiries,
        overdue_records=overdue_records[:10],
        tasks_due_this_month=filtered_tasks[:10]
    )

# Properties Routes
@api_router.get("/properties", response_model=List[PropertyResponse])
async def get_properties(search: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    query = {"user_id": current_user["id"]}
    if search:
        query["$or"] = [{"name": {"$regex": search, "$options": "i"}}, {"address": {"$regex": search, "$options": "i"}}, {"postcode": {"$regex": search, "$options": "i"}}]
    properties = await db.properties.find(query, {"_id": 0}).to_list(100)
    for prop in properties:
        prop["compliance_summary"] = await get_property_compliance_summary(prop["id"], current_user["id"])
    return properties

@api_router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, current_user: dict = Depends(get_current_user)):
    prop = await db.properties.find_one({"id": property_id, "user_id": current_user["id"]}, {"_id": 0})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    prop["compliance_summary"] = await get_property_compliance_summary(property_id, current_user["id"])
    return prop

@api_router.post("/properties", response_model=PropertyResponse)
async def create_property(property_data: PropertyCreate, current_user: dict = Depends(get_current_user)):
    # Validate required fields are not empty
    if not property_data.name or not property_data.name.strip():
        raise HTTPException(status_code=400, detail="Property name is required")
    if not property_data.address or not property_data.address.strip():
        raise HTTPException(status_code=400, detail="Address is required")
    if not property_data.postcode or not property_data.postcode.strip():
        raise HTTPException(status_code=400, detail="Postcode is required")
    
    now = datetime.now(timezone.utc).isoformat()
    property_id = str(uuid.uuid4())
    property_doc = {"id": property_id, "user_id": current_user["id"], "name": property_data.name.strip(), "address": property_data.address.strip(), "postcode": property_data.postcode.strip().upper(), "uk_nation": property_data.uk_nation, "is_in_london": property_data.is_in_london, "property_type": property_data.property_type, "ownership_type": property_data.ownership_type, "bedrooms": property_data.bedrooms, "notes": property_data.notes, "property_status": "active", "created_at": now, "updated_at": now}
    await db.properties.insert_one(property_doc)
    property_doc["compliance_summary"] = {"total": 0, "compliant": 0, "expiring_soon": 0, "overdue": 0, "missing": 0}
    return property_doc

@api_router.put("/properties/{property_id}", response_model=PropertyResponse)
async def update_property(property_id: str, property_data: PropertyUpdate, current_user: dict = Depends(get_current_user)):
    if not await db.properties.find_one({"id": property_id, "user_id": current_user["id"]}, {"_id": 0}):
        raise HTTPException(status_code=404, detail="Property not found")
    update_data = {k: v for k, v in property_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    if "postcode" in update_data:
        update_data["postcode"] = update_data["postcode"].upper()
    await db.properties.update_one({"id": property_id, "user_id": current_user["id"]}, {"$set": update_data})
    updated = await db.properties.find_one({"id": property_id, "user_id": current_user["id"]}, {"_id": 0})
    updated["compliance_summary"] = await get_property_compliance_summary(property_id, current_user["id"])
    return updated

@api_router.delete("/properties/{property_id}")
async def delete_property(property_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.properties.delete_one({"id": property_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Property not found")
    await db.compliance_records.delete_many({"property_id": property_id, "user_id": current_user["id"]})
    await db.tasks.delete_many({"property_id": property_id, "user_id": current_user["id"]})
    return {"message": "Property deleted successfully"}

# Property Compliance Report Export
@api_router.get("/properties/{property_id}/export")
async def export_property_report(property_id: str, current_user: dict = Depends(get_current_user)):
    """Generate and download a PDF compliance report for a property."""
    # Get property
    property_data = await db.properties.find_one(
        {"id": property_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not property_data:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Get compliance records
    compliance_records = await db.compliance_records.find(
        {"property_id": property_id, "user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(500)
    
    # Get tasks
    tasks = await db.tasks.find(
        {"property_id": property_id, "user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(500)
    
    # Get documents
    documents = await db.documents.find(
        {"property_id": property_id, "user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(500)
    
    # Get user preferences for company name
    user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "company_name": 1})
    company_name = user.get("company_name") if user else None
    
    # Generate PDF
    pdf_buffer = generate_compliance_report(
        property_data=property_data,
        compliance_records=compliance_records,
        tasks=tasks,
        documents=documents,
        company_name=company_name
    )
    
    # Create filename
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in property_data.get("name", "property"))
    filename = f"{safe_name}_compliance_report.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# Compliance Records Routes
@api_router.get("/compliance-records", response_model=List[ComplianceRecordResponse])
async def get_compliance_records(property_id: Optional[str] = None, category: Optional[str] = None, compliance_status: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    query = {"user_id": current_user["id"]}
    if property_id:
        query["property_id"] = property_id
    if category:
        query["category"] = category
    if compliance_status:
        query["compliance_status"] = compliance_status
    return await db.compliance_records.find(query, {"_id": 0}).to_list(500)

@api_router.get("/compliance-records/{record_id}", response_model=ComplianceRecordResponse)
async def get_compliance_record(record_id: str, current_user: dict = Depends(get_current_user)):
    record = await db.compliance_records.find_one({"id": record_id, "user_id": current_user["id"]}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    return record

@api_router.post("/compliance-records", response_model=ComplianceRecordResponse)
async def create_compliance_record(record_data: ComplianceRecordCreate, current_user: dict = Depends(get_current_user)):
    # Validate required fields
    if not record_data.title or not record_data.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    if not record_data.category or not record_data.category.strip():
        raise HTTPException(status_code=400, detail="Category is required")
    if not record_data.property_id or not record_data.property_id.strip():
        raise HTTPException(status_code=400, detail="Property ID is required")
    
    if not await db.properties.find_one({"id": record_data.property_id, "user_id": current_user["id"]}, {"_id": 0, "id": 1}):
        raise HTTPException(status_code=404, detail="Property not found")
    now = datetime.now(timezone.utc).isoformat()
    record_id = str(uuid.uuid4())
    record_doc = {"id": record_id, "user_id": current_user["id"], "property_id": record_data.property_id, "title": record_data.title.strip(), "category": record_data.category.strip(), "compliance_status": calculate_compliance_status(record_data.expiry_date, True), "issue_date": record_data.issue_date, "expiry_date": record_data.expiry_date, "reminder_preference": record_data.reminder_preference, "notes": record_data.notes, "created_at": now, "updated_at": now}
    await db.compliance_records.insert_one(record_doc)
    return record_doc

@api_router.put("/compliance-records/{record_id}", response_model=ComplianceRecordResponse)
async def update_compliance_record(record_id: str, record_data: ComplianceRecordUpdate, current_user: dict = Depends(get_current_user)):
    if not await db.compliance_records.find_one({"id": record_id, "user_id": current_user["id"]}, {"_id": 0}):
        raise HTTPException(status_code=404, detail="Compliance record not found")
    update_data = {k: v for k, v in record_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    if "expiry_date" in update_data:
        update_data["compliance_status"] = calculate_compliance_status(update_data["expiry_date"], True)
    await db.compliance_records.update_one({"id": record_id, "user_id": current_user["id"]}, {"$set": update_data})
    return await db.compliance_records.find_one({"id": record_id, "user_id": current_user["id"]}, {"_id": 0})

@api_router.delete("/compliance-records/{record_id}")
async def delete_compliance_record(record_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.compliance_records.delete_one({"id": record_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    return {"message": "Compliance record deleted successfully"}

# Tasks Routes
@api_router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    property_id: Optional[str] = None, 
    task_status: Optional[str] = None, 
    priority: Optional[str] = None,
    category: Optional[str] = None,
    filter_type: Optional[str] = None,  # overdue, due_soon, due_this_month
    current_user: dict = Depends(get_current_user)
):
    query = {"user_id": current_user["id"]}
    if property_id:
        query["property_id"] = property_id
    if task_status:
        query["task_status"] = task_status
    if priority:
        query["priority"] = priority
    if category:
        query["category"] = category
    
    tasks = await db.tasks.find(query, {"_id": 0}).to_list(500)
    
    # Apply date filters
    if filter_type:
        now = datetime.now(timezone.utc)
        filtered_tasks = []
        for task in tasks:
            if not task.get("due_date"):
                if filter_type == "no_date":
                    filtered_tasks.append(task)
                continue
            try:
                due = datetime.fromisoformat(task["due_date"].replace('Z', '+00:00'))
                if due.tzinfo is None:
                    due = due.replace(tzinfo=timezone.utc)
                
                if filter_type == "overdue" and due < now and task.get("task_status") != "completed":
                    filtered_tasks.append(task)
                elif filter_type == "due_soon" and 0 <= (due - now).days <= 7:
                    filtered_tasks.append(task)
                elif filter_type == "due_this_month":
                    month_end = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                    if now <= due <= month_end:
                        filtered_tasks.append(task)
            except (ValueError, TypeError):
                continue
        return filtered_tasks
    
    return tasks

@api_router.get("/tasks/templates")
async def get_task_templates():
    """Get common task templates for quick creation"""
    return [
        {"title": "Smoke & CO Alarm Check", "category": "safety", "priority": "high", "description": "Test all smoke and carbon monoxide alarms", "is_recurring": True, "recurrence_pattern": "monthly"},
        {"title": "Insurance Renewal Follow-up", "category": "renewal", "priority": "high", "description": "Review and renew landlord insurance policy"},
        {"title": "Licence Renewal Application", "category": "renewal", "priority": "urgent", "description": "Submit property licence renewal application"},
        {"title": "Fire Safety Inspection", "category": "inspection", "priority": "high", "description": "Conduct fire safety assessment and update equipment"},
        {"title": "Seasonal Property Review", "category": "seasonal", "priority": "medium", "description": "Check heating, gutters, and winter preparation", "is_recurring": True, "recurrence_pattern": "yearly"},
        {"title": "Gas Safety Certificate Booking", "category": "renewal", "priority": "urgent", "description": "Book annual gas safety inspection with registered engineer"},
        {"title": "EICR Inspection Booking", "category": "renewal", "priority": "high", "description": "Schedule 5-yearly electrical installation check"},
        {"title": "EPC Assessment Booking", "category": "renewal", "priority": "medium", "description": "Arrange energy performance certificate assessment"},
        {"title": "Legionella Risk Review", "category": "inspection", "priority": "medium", "description": "Review water system safety and legionella risk"},
        {"title": "PAT Testing Booking", "category": "inspection", "priority": "medium", "description": "Schedule portable appliance testing"}
    ]

@api_router.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, current_user: dict = Depends(get_current_user)):
    # Validate title
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(status_code=400, detail="Task title is required")
    
    now = datetime.now(timezone.utc).isoformat()
    task_doc = {
        "id": str(uuid.uuid4()), 
        "user_id": current_user["id"], 
        "property_id": task_data.property_id, 
        "title": task_data.title.strip(), 
        "description": task_data.description, 
        "due_date": task_data.due_date, 
        "priority": task_data.priority, 
        "task_status": "pending", 
        "category": task_data.category,
        "is_recurring": task_data.is_recurring,
        "recurrence_pattern": task_data.recurrence_pattern,
        "created_at": now, 
        "updated_at": now
    }
    await db.tasks.insert_one(task_doc)
    return task_doc

@api_router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate, current_user: dict = Depends(get_current_user)):
    existing = await db.tasks.find_one({"id": task_id, "user_id": current_user["id"]}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = {k: v for k, v in task_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # If completing a recurring task, create the next occurrence
    if task_data.task_status == "completed" and existing.get("is_recurring") and existing.get("recurrence_pattern"):
        await create_next_recurring_task(existing, current_user["id"])
    
    await db.tasks.update_one({"id": task_id, "user_id": current_user["id"]}, {"$set": update_data})
    return await db.tasks.find_one({"id": task_id, "user_id": current_user["id"]}, {"_id": 0})

async def create_next_recurring_task(original_task: dict, user_id: str):
    """Create the next occurrence of a recurring task"""
    pattern = original_task.get("recurrence_pattern", "monthly")
    due_date = original_task.get("due_date")
    
    if due_date:
        try:
            current_due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            if current_due.tzinfo is None:
                current_due = current_due.replace(tzinfo=timezone.utc)
            
            if pattern == "daily":
                next_due = current_due + timedelta(days=1)
            elif pattern == "weekly":
                next_due = current_due + timedelta(weeks=1)
            elif pattern == "monthly":
                next_due = current_due + timedelta(days=30)
            elif pattern == "yearly":
                next_due = current_due + timedelta(days=365)
            else:
                next_due = current_due + timedelta(days=30)
            
            due_date = next_due.isoformat()
        except (ValueError, TypeError):
            due_date = None
    
    now = datetime.now(timezone.utc).isoformat()
    new_task = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "property_id": original_task.get("property_id"),
        "title": original_task["title"],
        "description": original_task.get("description"),
        "due_date": due_date,
        "priority": original_task.get("priority", "medium"),
        "task_status": "pending",
        "category": original_task.get("category", "general"),
        "is_recurring": True,
        "recurrence_pattern": pattern,
        "created_at": now,
        "updated_at": now
    }
    await db.tasks.insert_one(new_task)

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.tasks.delete_one({"id": task_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

# Notifications Routes
@api_router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(unread_only: bool = False, current_user: dict = Depends(get_current_user)):
    query = {"user_id": current_user["id"]}
    if unread_only:
        query["is_read"] = False
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
    return notifications

@api_router.get("/notifications/generate")
async def generate_notifications(current_user: dict = Depends(get_current_user)):
    """Generate notifications based on compliance records and tasks - called on dashboard load"""
    user_id = current_user["id"]
    now = datetime.now(timezone.utc)
    notifications_created = 0
    
    # Get user preferences
    prefs = await db.user_preferences.find_one({"user_id": user_id}, {"_id": 0})
    if prefs and not prefs.get("inapp_reminders", True):
        return {"message": "In-app reminders disabled", "created": 0}
    
    reminder_days = prefs.get("reminder_lead_days", [90, 60, 30, 7]) if prefs else [90, 60, 30, 7]
    
    # Get properties for name lookup
    properties = await db.properties.find({"user_id": user_id}, {"_id": 0, "id": 1, "name": 1}).to_list(100)
    prop_map = {p["id"]: p["name"] for p in properties}
    
    # Check compliance records for expiry reminders
    compliance_records = await db.compliance_records.find(
        {"user_id": user_id, "expiry_date": {"$ne": None}}, 
        {"_id": 0}
    ).to_list(500)
    
    for record in compliance_records:
        try:
            expiry = datetime.fromisoformat(record["expiry_date"].replace('Z', '+00:00'))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            days_until = (expiry - now).days
            
            # Check if we should create a notification for this record
            for lead_days in reminder_days:
                if days_until == lead_days or (days_until < 0 and lead_days == 0):
                    # Check if notification already exists
                    existing = await db.notifications.find_one({
                        "user_id": user_id,
                        "reference_id": record["id"],
                        "notification_type": "expiry_reminder" if days_until >= 0 else "overdue_alert"
                    })
                    
                    if not existing:
                        prop_name = prop_map.get(record["property_id"], "Unknown Property")
                        if days_until < 0:
                            title = f"{record['title']} is overdue"
                            message = f"The {record['title']} for {prop_name} expired {abs(days_until)} days ago."
                            notification_type = "overdue_alert"
                        elif days_until == 0:
                            title = f"{record['title']} expires today"
                            message = f"The {record['title']} for {prop_name} expires today!"
                            notification_type = "expiry_reminder"
                        else:
                            title = f"{record['title']} expires in {days_until} days"
                            message = f"The {record['title']} for {prop_name} will expire on {expiry.strftime('%d %b %Y')}."
                            notification_type = "expiry_reminder"
                        
                        await db.notifications.insert_one({
                            "id": str(uuid.uuid4()),
                            "user_id": user_id,
                            "notification_type": notification_type,
                            "title": title,
                            "message": message,
                            "reference_type": "compliance_record",
                            "reference_id": record["id"],
                            "is_read": False,
                            "created_at": now.isoformat()
                        })
                        notifications_created += 1
                    break
        except (ValueError, TypeError):
            continue
    
    # Check tasks for due date reminders
    tasks = await db.tasks.find(
        {"user_id": user_id, "task_status": {"$in": ["pending", "in_progress"]}, "due_date": {"$ne": None}},
        {"_id": 0}
    ).to_list(500)
    
    for task in tasks:
        try:
            due = datetime.fromisoformat(task["due_date"].replace('Z', '+00:00'))
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            days_until = (due - now).days
            
            # Create notification for overdue or due soon tasks
            if days_until <= 1:
                existing = await db.notifications.find_one({
                    "user_id": user_id,
                    "reference_id": task["id"],
                    "notification_type": "task_due"
                })
                
                if not existing:
                    if days_until < 0:
                        title = f"Task overdue: {task['title']}"
                        message = f"This task was due {abs(days_until)} days ago."
                    elif days_until == 0:
                        title = f"Task due today: {task['title']}"
                        message = "This task is due today."
                    else:
                        title = f"Task due tomorrow: {task['title']}"
                        message = "This task is due tomorrow."
                    
                    await db.notifications.insert_one({
                        "id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "notification_type": "task_due",
                        "title": title,
                        "message": message,
                        "reference_type": "task",
                        "reference_id": task["id"],
                        "is_read": False,
                        "created_at": now.isoformat()
                    })
                    notifications_created += 1
        except (ValueError, TypeError):
            continue
    
    return {"message": "Notifications generated", "created": notifications_created}

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"is_read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@api_router.put("/notifications/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": current_user["id"], "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"message": "All notifications marked as read"}

@api_router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.delete_one({"id": notification_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}

# User Preferences Routes
@api_router.get("/user/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(current_user: dict = Depends(get_current_user)):
    prefs = await db.user_preferences.find_one({"user_id": current_user["id"]}, {"_id": 0})
    if not prefs:
        return UserPreferencesResponse()
    return UserPreferencesResponse(
        email_reminders=prefs.get("email_reminders", True),
        inapp_reminders=prefs.get("inapp_reminders", True),
        reminder_lead_days=prefs.get("reminder_lead_days", [90, 60, 30, 7]),
        company_name=prefs.get("company_name"),
        weekly_digest=prefs.get("weekly_digest", True),
        marketing_emails=prefs.get("marketing_emails", False)
    )

@api_router.put("/user/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(prefs_data: UserPreferencesUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in prefs_data.model_dump().items() if v is not None}
    update_data["user_id"] = current_user["id"]
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.user_preferences.update_one(
        {"user_id": current_user["id"]},
        {"$set": update_data},
        upsert=True
    )
    
    # Also update company_name on user record for PDF reports
    if "company_name" in update_data:
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": {"company_name": update_data["company_name"]}}
        )
    
    prefs = await db.user_preferences.find_one({"user_id": current_user["id"]}, {"_id": 0})
    return UserPreferencesResponse(
        email_reminders=prefs.get("email_reminders", True),
        inapp_reminders=prefs.get("inapp_reminders", True),
        reminder_lead_days=prefs.get("reminder_lead_days", [90, 60, 30, 7]),
        company_name=prefs.get("company_name"),
        weekly_digest=prefs.get("weekly_digest", True),
        marketing_emails=prefs.get("marketing_emails", False)
    )

# Contact Form
@api_router.post("/contact")
async def submit_contact_form(form_data: ContactFormRequest, current_user: dict = Depends(get_current_user)):
    """Submit a support/contact request."""
    now = datetime.now(timezone.utc).isoformat()
    contact_id = str(uuid.uuid4())
    
    contact_doc = {
        "id": contact_id,
        "user_id": current_user["id"],
        "user_email": current_user["email"],
        "subject": form_data.subject,
        "message": form_data.message,
        "contact_type": form_data.contact_type,
        "status": "pending",
        "created_at": now
    }
    
    await db.contact_requests.insert_one(contact_doc)
    
    return {
        "success": True,
        "message": "Thank you for contacting us. We'll get back to you within 24 hours.",
        "ticket_id": contact_id
    }

# Subscription Management Routes
@api_router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(current_user: dict = Depends(get_current_user)):
    """Get current user's subscription details"""
    plan = current_user.get("subscription_plan", "solo")
    status = current_user.get("subscription_status", "trial")
    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["solo"])
    
    # Check if trial expired
    if status == "trial" and current_user.get("trial_end"):
        trial_end = datetime.fromisoformat(current_user["trial_end"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > trial_end:
            status = "expired"
            await db.users.update_one({"id": current_user["id"]}, {"$set": {"subscription_status": "expired"}})
    
    property_count = await db.properties.count_documents({"user_id": current_user["id"], "property_status": "active"})
    
    # Calculate trial days remaining
    trial_days_remaining = None
    if status == "trial" and current_user.get("trial_end"):
        trial_end = datetime.fromisoformat(current_user["trial_end"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        trial_days_remaining = max(0, (trial_end - datetime.now(timezone.utc)).days)
    
    # Determine upgrade/downgrade options
    plan_order = ["solo", "portfolio", "operator"]
    current_idx = plan_order.index(plan) if plan in plan_order else 0
    can_upgrade = current_idx < len(plan_order) - 1
    can_downgrade = current_idx > 0 and property_count <= SUBSCRIPTION_PLANS[plan_order[current_idx - 1]]["property_limit"]
    
    return SubscriptionResponse(
        plan=plan,
        plan_name=plan_info["name"],
        status=status,
        property_limit=plan_info["property_limit"],
        property_count=property_count,
        trial_start=current_user.get("trial_start"),
        trial_end=current_user.get("trial_end"),
        trial_days_remaining=trial_days_remaining,
        price_monthly=plan_info["price_monthly"],
        price_yearly=plan_info["price_yearly"],
        features=plan_info["features"],
        can_upgrade=can_upgrade,
        can_downgrade=can_downgrade
    )

@api_router.get("/subscription/plans")
async def get_subscription_plans():
    """Get all available subscription plans"""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "trial_days": TRIAL_DAYS
    }

@api_router.post("/subscription/change", response_model=SubscriptionResponse)
async def change_subscription(update: SubscriptionUpdate, current_user: dict = Depends(get_current_user)):
    """Change subscription plan (upgrade or downgrade)"""
    new_plan = update.plan.lower()
    if new_plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan selected")
    
    new_plan_info = SUBSCRIPTION_PLANS[new_plan]
    
    # Check if downgrade is possible (property count must be within new limit)
    property_count = await db.properties.count_documents({"user_id": current_user["id"], "property_status": "active"})
    if property_count > new_plan_info["property_limit"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot downgrade to {new_plan_info['name']} plan. You have {property_count} properties but the limit is {new_plan_info['property_limit']}. Please remove some properties first."
        )
    
    # Update subscription
    now = datetime.now(timezone.utc).isoformat()
    update_data = {
        "subscription_plan": new_plan,
        "subscription_status": "active",  # Changing plan activates subscription
        "updated_at": now
    }
    
    await db.users.update_one({"id": current_user["id"]}, {"$set": update_data})
    
    # Return updated subscription
    plan_order = ["solo", "portfolio", "operator"]
    current_idx = plan_order.index(new_plan) if new_plan in plan_order else 0
    can_upgrade = current_idx < len(plan_order) - 1
    can_downgrade = current_idx > 0 and property_count <= SUBSCRIPTION_PLANS[plan_order[current_idx - 1]]["property_limit"]
    
    return SubscriptionResponse(
        plan=new_plan,
        plan_name=new_plan_info["name"],
        status="active",
        property_limit=new_plan_info["property_limit"],
        property_count=property_count,
        trial_start=current_user.get("trial_start"),
        trial_end=current_user.get("trial_end"),
        trial_days_remaining=None,
        price_monthly=new_plan_info["price_monthly"],
        price_yearly=new_plan_info["price_yearly"],
        features=new_plan_info["features"],
        can_upgrade=can_upgrade,
        can_downgrade=can_downgrade
    )

@api_router.get("/subscription/check-limit", response_model=PlanLimitCheck)
async def check_property_limit(current_user: dict = Depends(get_current_user)):
    """Check if user can add another property based on their plan"""
    plan = current_user.get("subscription_plan", "solo")
    status = current_user.get("subscription_status", "trial")
    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["solo"])
    
    property_count = await db.properties.count_documents({"user_id": current_user["id"], "property_status": "active"})
    property_limit = plan_info["property_limit"]
    
    # Check if trial expired
    if status == "trial" and current_user.get("trial_end"):
        trial_end = datetime.fromisoformat(current_user["trial_end"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > trial_end:
            return PlanLimitCheck(
                allowed=False,
                current_count=property_count,
                limit=property_limit,
                plan=plan,
                message="Your trial has expired. Please upgrade to continue using Staylet."
            )
    
    if property_count >= property_limit:
        next_plan = None
        plan_order = ["solo", "portfolio", "operator"]
        current_idx = plan_order.index(plan) if plan in plan_order else 0
        if current_idx < len(plan_order) - 1:
            next_plan = plan_order[current_idx + 1]
            next_plan_info = SUBSCRIPTION_PLANS[next_plan]
            return PlanLimitCheck(
                allowed=False,
                current_count=property_count,
                limit=property_limit,
                plan=plan,
                message=f"You've reached the {property_limit} property limit on your {plan_info['name']} plan. Upgrade to {next_plan_info['name']} for up to {next_plan_info['property_limit']} properties."
            )
        else:
            return PlanLimitCheck(
                allowed=False,
                current_count=property_count,
                limit=property_limit,
                plan=plan,
                message=f"You've reached the maximum of {property_limit} properties on the {plan_info['name']} plan. Contact support for enterprise options."
            )
    
    return PlanLimitCheck(
        allowed=True,
        current_count=property_count,
        limit=property_limit,
        plan=plan,
        message=None
    )

# Stripe Payment Routes
@api_router.post("/payments/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: Request,
    checkout_request: CheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a Stripe checkout session for subscription payment."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    # Validate plan
    plan = checkout_request.plan.lower()
    if plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan selected")
    
    plan_info = SUBSCRIPTION_PLANS[plan]
    billing_cycle = checkout_request.billing_cycle.lower()
    
    # Get amount based on billing cycle (amounts must be floats for Stripe)
    if billing_cycle == "annual":
        amount = float(plan_info["price_yearly"])
    else:
        amount = float(plan_info["price_monthly"])
    
    # Build success and cancel URLs from frontend origin
    origin_url = checkout_request.origin_url.rstrip('/')
    success_url = f"{origin_url}/app/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/app/billing"
    
    # Initialize Stripe checkout
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Create checkout session
    session_id = str(uuid.uuid4())
    metadata = {
        "user_id": current_user["id"],
        "user_email": current_user["email"],
        "plan": plan,
        "billing_cycle": billing_cycle,
        "internal_session_id": session_id
    }
    
    checkout_req = CheckoutSessionRequest(
        amount=amount,
        currency="gbp",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata
    )
    
    try:
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_req)
        
        # Create payment transaction record
        now = datetime.now(timezone.utc).isoformat()
        transaction = {
            "id": session_id,
            "stripe_session_id": session.session_id,
            "user_id": current_user["id"],
            "user_email": current_user["email"],
            "plan": plan,
            "billing_cycle": billing_cycle,
            "amount": amount,
            "currency": "gbp",
            "payment_status": "pending",
            "status": "initiated",
            "created_at": now,
            "updated_at": now
        }
        await db.payment_transactions.insert_one(transaction)
        
        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.session_id
        )
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@api_router.get("/payments/status/{session_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get payment status and update subscription if paid."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    # Find the transaction
    transaction = await db.payment_transactions.find_one(
        {"stripe_session_id": session_id},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Payment session not found")
    
    # Check if already processed
    if transaction.get("payment_status") == "paid":
        return PaymentStatusResponse(
            status="complete",
            payment_status="paid",
            plan=transaction.get("plan"),
            billing_cycle=transaction.get("billing_cycle"),
            success=True,
            message="Payment already processed"
        )
    
    # Initialize Stripe checkout
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Update transaction status
        await db.payment_transactions.update_one(
            {"stripe_session_id": session_id},
            {"$set": {
                "payment_status": status.payment_status,
                "status": status.status,
                "updated_at": now
            }}
        )
        
        # If payment successful, update user subscription
        if status.payment_status == "paid":
            plan = transaction.get("plan", "solo")
            billing_cycle = transaction.get("billing_cycle", "monthly")
            
            # Calculate subscription end date
            if billing_cycle == "annual":
                subscription_end = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
            else:
                subscription_end = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
            
            # Update user subscription
            await db.users.update_one(
                {"id": transaction["user_id"]},
                {"$set": {
                    "subscription_plan": plan,
                    "subscription_status": "active",
                    "subscription_start": now,
                    "subscription_end": subscription_end,
                    "billing_cycle": billing_cycle,
                    "updated_at": now
                }}
            )
            
            return PaymentStatusResponse(
                status=status.status,
                payment_status=status.payment_status,
                plan=plan,
                billing_cycle=billing_cycle,
                success=True,
                message=f"Successfully subscribed to {SUBSCRIPTION_PLANS[plan]['name']} plan!"
            )
        elif status.status == "expired":
            return PaymentStatusResponse(
                status=status.status,
                payment_status=status.payment_status,
                success=False,
                message="Payment session expired. Please try again."
            )
        else:
            return PaymentStatusResponse(
                status=status.status,
                payment_status=status.payment_status,
                success=False,
                message="Payment is being processed..."
            )
    except Exception as e:
        logger.error(f"Stripe status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check payment status: {str(e)}")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    # Get webhook body and signature
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    # Initialize Stripe checkout
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Update transaction based on webhook event
        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {"stripe_session_id": webhook_response.session_id},
                {"$set": {
                    "payment_status": webhook_response.payment_status,
                    "webhook_event_type": webhook_response.event_type,
                    "webhook_event_id": webhook_response.event_id,
                    "updated_at": now
                }}
            )
            
            # If payment successful via webhook, update user subscription
            if webhook_response.payment_status == "paid":
                transaction = await db.payment_transactions.find_one(
                    {"stripe_session_id": webhook_response.session_id},
                    {"_id": 0}
                )
                
                if transaction:
                    plan = transaction.get("plan", "solo")
                    billing_cycle = transaction.get("billing_cycle", "monthly")
                    
                    # Calculate subscription end date
                    if billing_cycle == "annual":
                        subscription_end = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
                    else:
                        subscription_end = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                    
                    await db.users.update_one(
                        {"id": transaction["user_id"]},
                        {"$set": {
                            "subscription_plan": plan,
                            "subscription_status": "active",
                            "subscription_start": now,
                            "subscription_end": subscription_end,
                            "billing_cycle": billing_cycle,
                            "updated_at": now
                        }}
                    )
        
        return {"received": True}
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

@api_router.get("/constants")
async def get_constants():
    return {
        "uk_nations": UK_NATIONS, 
        "property_types": PROPERTY_TYPES, 
        "ownership_types": OWNERSHIP_TYPES, 
        "compliance_categories": COMPLIANCE_CATEGORIES, 
        "compliance_status": COMPLIANCE_STATUS, 
        "reminder_options": REMINDER_OPTIONS,
        "task_statuses": TASK_STATUSES,
        "task_priorities": TASK_PRIORITIES,
        "task_categories": TASK_CATEGORIES,
        "notification_types": NOTIFICATION_TYPES,
        "reminder_intervals": REMINDER_INTERVALS,
        "allowed_file_types": list(ALLOWED_FILE_TYPES.keys()),
        "max_file_size": MAX_FILE_SIZE,
        "subscription_plans": SUBSCRIPTION_PLANS,
        "trial_days": TRIAL_DAYS
    }

# Document Upload and Extraction Routes
@api_router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    compliance_record_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document file. Optionally link to a compliance record."""
    # Validate file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed. Allowed types: PDF, PNG, JPG")
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Generate unique filename
    file_ext = ALLOWED_FILE_TYPES[file.content_type]
    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / stored_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Store document metadata
    now = datetime.now(timezone.utc).isoformat()
    doc_record = {
        "id": file_id,
        "user_id": current_user["id"],
        "compliance_record_id": compliance_record_id,
        "filename": stored_filename,
        "original_filename": file.filename,
        "file_type": file.content_type,
        "file_size": len(content),
        "uploaded_at": now
    }
    
    await db.documents.insert_one(doc_record)
    
    return DocumentResponse(**doc_record)

@api_router.post("/documents/upload-and-extract")
async def upload_and_extract_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document and extract compliance information using AI."""
    # Validate file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed. Allowed types: PDF, PNG, JPG")
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Generate unique filename
    file_ext = ALLOWED_FILE_TYPES[file.content_type]
    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / stored_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Store document metadata (not linked to compliance record yet)
    now = datetime.now(timezone.utc).isoformat()
    doc_record = {
        "id": file_id,
        "user_id": current_user["id"],
        "compliance_record_id": None,  # Will be linked after user confirms
        "filename": stored_filename,
        "original_filename": file.filename,
        "file_type": file.content_type,
        "file_size": len(content),
        "uploaded_at": now
    }
    
    await db.documents.insert_one(doc_record)
    
    # Encode file to base64 for extraction
    file_base64 = base64.b64encode(content).decode('utf-8')
    
    # Run extraction
    extraction_result = await extract_document_info(file_base64, file.filename, file.content_type)
    formatted_result = format_extracted_for_ui(extraction_result)
    
    # If extraction failed, try filename-based suggestion
    if not formatted_result.get("success") or not formatted_result.get("suggestions", {}).get("category"):
        suggested_category = suggest_category_from_filename(file.filename)
        if suggested_category:
            if "suggestions" not in formatted_result:
                formatted_result["suggestions"] = {}
            formatted_result["suggestions"]["category"] = {
                "value": suggested_category,
                "label": "Suggested from filename",
                "confidence": "LOW",
                "is_suggested": True
            }
    
    return {
        "document": DocumentResponse(**doc_record),
        "extraction": formatted_result
    }

@api_router.get("/documents/{document_id}")
async def get_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Get document metadata."""
    doc = await db.documents.find_one(
        {"id": document_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(**doc)

@api_router.get("/documents/{document_id}/download")
async def download_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Download a document file."""
    doc = await db.documents.find_one(
        {"id": document_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = UPLOAD_DIR / doc["filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=str(file_path),
        filename=doc["original_filename"],
        media_type=doc["file_type"]
    )

@api_router.get("/compliance-records/{record_id}/documents", response_model=List[DocumentResponse])
async def get_compliance_record_documents(record_id: str, current_user: dict = Depends(get_current_user)):
    """Get all documents for a compliance record."""
    documents = await db.documents.find(
        {"compliance_record_id": record_id, "user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    return documents

@api_router.put("/documents/{document_id}/link")
async def link_document_to_record(
    document_id: str, 
    compliance_record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Link an uploaded document to a compliance record."""
    # Verify document exists and belongs to user
    doc = await db.documents.find_one(
        {"id": document_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify compliance record exists and belongs to user
    record = await db.compliance_records.find_one(
        {"id": compliance_record_id, "user_id": current_user["id"]},
        {"_id": 0, "id": 1}
    )
    if not record:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    
    # Update document
    await db.documents.update_one(
        {"id": document_id, "user_id": current_user["id"]},
        {"$set": {"compliance_record_id": compliance_record_id}}
    )
    
    return {"message": "Document linked successfully"}

@api_router.delete("/documents/{document_id}")
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a document."""
    doc = await db.documents.find_one(
        {"id": document_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    file_path = UPLOAD_DIR / doc["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database
    await db.documents.delete_one({"id": document_id, "user_id": current_user["id"]})
    
    return {"message": "Document deleted successfully"}

# AI Assistant Routes
class AssistantQueryRequest(BaseModel):
    question: str

@api_router.get("/assistant/insights")
async def get_assistant_insights(current_user: dict = Depends(get_current_user)):
    """Get structured compliance insights for the dashboard."""
    insights = await get_structured_insights(db, current_user["id"])
    return insights

@api_router.get("/assistant/property/{property_id}")
async def get_property_assistant_insights(property_id: str, current_user: dict = Depends(get_current_user)):
    """Get AI insights for a specific property."""
    insights = await get_property_insights(db, current_user["id"], property_id)
    if "error" in insights:
        raise HTTPException(status_code=404, detail=insights["error"])
    return insights

@api_router.post("/assistant/ask")
async def ask_assistant(request: AssistantQueryRequest, current_user: dict = Depends(get_current_user)):
    """Ask a natural language question about compliance data."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    response = await answer_natural_language_query(db, current_user["id"], request.question)
    return response

@api_router.get("/")
async def root():
    return {"message": "Staylet API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','), allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
