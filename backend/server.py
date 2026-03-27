from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'staylet-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI(title="Staylet API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ MODELS ============

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

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

# Subscription Models
class Subscription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tier: str = "free"  # free, starter, professional, business
    subscription_status: str = "active"  # active, cancelled, expired
    properties_limit: int = 1
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None

# Property Models
class Property(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    address: str
    postcode: str
    property_type: str = "apartment"  # apartment, house, studio, other
    bedrooms: int = 1
    property_status: str = "active"  # active, inactive, archived
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PropertyCreate(BaseModel):
    name: str
    address: str
    postcode: str
    property_type: str = "apartment"
    bedrooms: int = 1

# Compliance Record Models
class ComplianceRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    property_id: str
    document_type: str  # gas_safety, epc, eicr, pat, fire_safety, insurance, license
    document_name: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    compliance_status: str = "valid"  # valid, expiring_soon, expired, missing
    file_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Task Models
class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    property_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"  # low, medium, high, urgent
    task_status: str = "pending"  # pending, in_progress, completed, cancelled
    category: str = "general"  # compliance, maintenance, admin, other
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TaskCreate(BaseModel):
    property_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"
    category: str = "general"

# Notification Models
class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    message: str
    type: str = "info"  # info, warning, error, success
    read: bool = False
    link: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Uploaded File Models
class UploadedFile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    property_id: Optional[str] = None
    compliance_record_id: Optional[str] = None
    filename: str
    file_type: str
    file_size: int
    storage_path: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Dashboard Stats Model
class DashboardStats(BaseModel):
    total_properties: int = 0
    upcoming_expiries: int = 0
    overdue_items: int = 0
    missing_documents: int = 0
    tasks_due: int = 0

# ============ AUTH HELPERS ============

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_token(token)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ============ AUTH ROUTES ============

@api_router.post("/auth/signup", response_model=AuthResponse)
async def signup(user_data: UserCreate):
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": user_data.email.lower(),
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "subscription_tier": "free",
        "created_at": now,
        "updated_at": now
    }
    
    await db.users.insert_one(user_doc)
    
    # Create default subscription
    subscription_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "tier": "free",
        "subscription_status": "active",
        "properties_limit": 1,
        "created_at": now
    }
    await db.subscriptions.insert_one(subscription_doc)
    
    # Generate token
    token = create_token(user_id, user_data.email.lower())
    
    user_response = UserResponse(
        id=user_id,
        email=user_data.email.lower(),
        full_name=user_data.full_name,
        created_at=now,
        subscription_tier="free"
    )
    
    return AuthResponse(user=user_response, token=token)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email.lower()}, {"_id": 0})
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user["id"], user["email"])
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"],
        subscription_tier=user.get("subscription_tier", "free")
    )
    
    return AuthResponse(user=user_response, token=token)

@api_router.post("/auth/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: PasswordResetRequest):
    # Check if user exists (not used, to prevent email enumeration)
    _ = await db.users.find_one({"email": request.email.lower()})
    
    # Always return success to prevent email enumeration
    # In production, this would send an actual email
    logger.info(f"Password reset requested for: {request.email}")
    
    return PasswordResetResponse(
        message="If an account exists with this email, you will receive password reset instructions.",
        success=True
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        created_at=current_user["created_at"],
        subscription_tier=current_user.get("subscription_tier", "free")
    )

# ============ DASHBOARD ROUTES ============

@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # Count properties
    total_properties = await db.properties.count_documents({"user_id": user_id, "property_status": "active"})
    
    # Count upcoming expiries (within 30 days)
    upcoming_expiries = await db.compliance_records.count_documents({
        "user_id": user_id,
        "compliance_status": "expiring_soon"
    })
    
    # Count overdue items
    overdue_items = await db.compliance_records.count_documents({
        "user_id": user_id,
        "compliance_status": "expired"
    })
    
    # Count missing documents
    missing_documents = await db.compliance_records.count_documents({
        "user_id": user_id,
        "compliance_status": "missing"
    })
    
    # Count pending tasks due soon
    tasks_due = await db.tasks.count_documents({
        "user_id": user_id,
        "task_status": {"$in": ["pending", "in_progress"]}
    })
    
    return DashboardStats(
        total_properties=total_properties,
        upcoming_expiries=upcoming_expiries,
        overdue_items=overdue_items,
        missing_documents=missing_documents,
        tasks_due=tasks_due
    )

# ============ PROPERTIES ROUTES ============

@api_router.get("/properties", response_model=List[Property])
async def get_properties(current_user: dict = Depends(get_current_user)):
    properties = await db.properties.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    return properties

@api_router.post("/properties", response_model=Property)
async def create_property(property_data: PropertyCreate, current_user: dict = Depends(get_current_user)):
    now = datetime.now(timezone.utc).isoformat()
    
    property_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "name": property_data.name,
        "address": property_data.address,
        "postcode": property_data.postcode,
        "property_type": property_data.property_type,
        "bedrooms": property_data.bedrooms,
        "property_status": "active",
        "created_at": now,
        "updated_at": now
    }
    
    await db.properties.insert_one(property_doc)
    return Property(**property_doc)

# ============ TASKS ROUTES ============

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user: dict = Depends(get_current_user)):
    tasks = await db.tasks.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    return tasks

@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, current_user: dict = Depends(get_current_user)):
    now = datetime.now(timezone.utc).isoformat()
    
    task_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "property_id": task_data.property_id,
        "title": task_data.title,
        "description": task_data.description,
        "due_date": task_data.due_date,
        "priority": task_data.priority,
        "task_status": "pending",
        "category": task_data.category,
        "created_at": now,
        "updated_at": now
    }
    
    await db.tasks.insert_one(task_doc)
    return Task(**task_doc)

# ============ NOTIFICATIONS ROUTES ============

@api_router.get("/notifications", response_model=List[Notification])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return notifications

# ============ HEALTH CHECK ============

@api_router.get("/")
async def root():
    return {"message": "Staylet API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
