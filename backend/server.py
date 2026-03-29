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

# Import modular routes
from routes.auth import router as auth_router
from routes.properties import router as properties_router
from routes.compliance import router as compliance_router
from routes.tasks import router as tasks_router
from routes.notifications import router as notifications_router
from routes.billing import router as billing_router

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

# Include modular routers
api_router.include_router(auth_router)
api_router.include_router(properties_router)
api_router.include_router(compliance_router)
api_router.include_router(tasks_router)
api_router.include_router(notifications_router)
api_router.include_router(billing_router)

app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','), allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
