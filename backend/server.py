from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import base64
import aiofiles
from document_extraction import extract_document_info, format_extracted_for_ui, suggest_category_from_filename

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
    subscription_tier: str = "free"

class AuthResponse(BaseModel):
    user: UserResponse
    token: str

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

class UserPreferencesResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    email_reminders: bool = True
    inapp_reminders: bool = True
    reminder_lead_days: List[int] = [90, 60, 30, 7]

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
    now = datetime.now(timezone.utc).isoformat()
    user_doc = {"id": user_id, "email": user_data.email.lower(), "password": hash_password(user_data.password), "full_name": user_data.full_name, "subscription_tier": "free", "created_at": now, "updated_at": now}
    await db.users.insert_one(user_doc)
    token = create_token(user_id, user_data.email.lower())
    return AuthResponse(user=UserResponse(id=user_id, email=user_data.email.lower(), full_name=user_data.full_name, created_at=now, subscription_tier="free"), token=token)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email.lower()}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user["id"], user["email"])
    return AuthResponse(user=UserResponse(id=user["id"], email=user["email"], full_name=user["full_name"], created_at=user["created_at"], subscription_tier=user.get("subscription_tier", "free")), token=token)

@api_router.post("/auth/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: PasswordResetRequest):
    _ = await db.users.find_one({"email": request.email.lower()})
    return PasswordResetResponse(message="If an account exists with this email, you will receive password reset instructions.", success=True)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(id=current_user["id"], email=current_user["email"], full_name=current_user["full_name"], created_at=current_user["created_at"], subscription_tier=current_user.get("subscription_tier", "free"))

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
        reminder_lead_days=prefs.get("reminder_lead_days", [90, 60, 30, 7])
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
    
    prefs = await db.user_preferences.find_one({"user_id": current_user["id"]}, {"_id": 0})
    return UserPreferencesResponse(
        email_reminders=prefs.get("email_reminders", True),
        inapp_reminders=prefs.get("inapp_reminders", True),
        reminder_lead_days=prefs.get("reminder_lead_days", [90, 60, 30, 7])
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
        "max_file_size": MAX_FILE_SIZE
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
