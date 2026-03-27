from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

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

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    task_status: Optional[str] = None

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
    created_at: str
    updated_at: str

class DashboardStats(BaseModel):
    total_properties: int = 0
    upcoming_expiries: int = 0
    overdue_items: int = 0
    missing_records: int = 0
    tasks_due: int = 0

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
    return DashboardStats(total_properties=total_properties, upcoming_expiries=upcoming_expiries, overdue_items=overdue_items, missing_records=missing_records, tasks_due=tasks_due)

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
async def get_tasks(property_id: Optional[str] = None, task_status: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    query = {"user_id": current_user["id"]}
    if property_id:
        query["property_id"] = property_id
    if task_status:
        query["task_status"] = task_status
    return await db.tasks.find(query, {"_id": 0}).to_list(100)

@api_router.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, current_user: dict = Depends(get_current_user)):
    now = datetime.now(timezone.utc).isoformat()
    task_doc = {"id": str(uuid.uuid4()), "user_id": current_user["id"], "property_id": task_data.property_id, "title": task_data.title, "description": task_data.description, "due_date": task_data.due_date, "priority": task_data.priority, "task_status": "pending", "category": task_data.category, "created_at": now, "updated_at": now}
    await db.tasks.insert_one(task_doc)
    return task_doc

@api_router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate, current_user: dict = Depends(get_current_user)):
    if not await db.tasks.find_one({"id": task_id, "user_id": current_user["id"]}, {"_id": 0}):
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = {k: v for k, v in task_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.tasks.update_one({"id": task_id, "user_id": current_user["id"]}, {"$set": update_data})
    return await db.tasks.find_one({"id": task_id, "user_id": current_user["id"]}, {"_id": 0})

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.tasks.delete_one({"id": task_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

# Other Routes
@api_router.get("/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    return await db.notifications.find({"user_id": current_user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)

@api_router.get("/constants")
async def get_constants():
    return {"uk_nations": UK_NATIONS, "property_types": PROPERTY_TYPES, "ownership_types": OWNERSHIP_TYPES, "compliance_categories": COMPLIANCE_CATEGORIES, "compliance_status": COMPLIANCE_STATUS, "reminder_options": REMINDER_OPTIONS}

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
