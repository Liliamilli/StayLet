"""
Authentication routes for Staylet.
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
import uuid

from models.database import db
from models.schemas import (
    UserCreate, UserLogin, UserResponse, AuthResponse,
    PasswordResetRequest, PasswordResetResponse, ChangePasswordRequest
)
from utils.auth import hash_password, verify_password, create_token, get_current_user
from utils.constants import SUBSCRIPTION_PLANS, TRIAL_DAYS
from utils.email_service import send_email, get_password_reset_email, get_welcome_email, is_email_configured
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserCreate):
    """Create a new user account."""
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
    plan_info = SUBSCRIPTION_PLANS.get("solo", {})
    
    # Send welcome email if configured
    if is_email_configured():
        frontend_url = os.environ.get('FRONTEND_URL', 'https://staylet.app')
        dashboard_link = f"{frontend_url}/app"
        subject, html = get_welcome_email(user_data.full_name.split()[0], dashboard_link)
        # Fire and forget - don't block signup on email
        await send_email(user_data.email.lower(), subject, html)
    
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
            property_count=0
        ), 
        token=token
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """Login with email and password."""
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


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: PasswordResetRequest):
    """Request a password reset email."""
    user = await db.users.find_one({"email": request.email.lower()}, {"_id": 0})
    
    # Always return success message to prevent email enumeration
    response_message = "If an account exists with this email, you will receive password reset instructions."
    
    if user and is_email_configured():
        # Generate reset token (simple approach - in production use JWT with expiry)
        reset_token = str(uuid.uuid4())
        await db.users.update_one(
            {"email": request.email.lower()},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_expiry": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            }}
        )
        
        # Build reset link
        frontend_url = os.environ.get('FRONTEND_URL', 'https://staylet.app')
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        # Send email
        user_name = user.get("full_name", "").split()[0] or "there"
        subject, html = get_password_reset_email(reset_link, user_name)
        await send_email(request.email.lower(), subject, html)
    
    return PasswordResetResponse(message=response_message, success=True)


@router.post("/change-password")
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


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
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


@router.post("/demo", response_model=AuthResponse)
async def create_demo_account():
    """Create a demo account with realistic sample data for UK short-let properties."""
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
         "expiry_date": (now + timedelta(days=45)).date().isoformat(),
         "notes": "Annual inspection by British Gas engineer"},
        {"property_id": property_ids[0], "title": "EICR Certificate", "category": "eicr", 
         "expiry_date": (now + timedelta(days=400)).date().isoformat(),
         "notes": "5-year electrical inspection completed"},
        {"property_id": property_ids[0], "title": "EPC Rating", "category": "epc", 
         "expiry_date": (now + timedelta(days=1200)).date().isoformat(),
         "notes": "Rating: C (72)"},
        {"property_id": property_ids[0], "title": "Landlord Insurance", "category": "insurance", 
         "expiry_date": (now - timedelta(days=5)).date().isoformat(),
         "notes": "Buildings and contents with Aviva - RENEWAL NEEDED"},
        
        # Property 2 - Cotswold Cottage (mostly compliant)
        {"property_id": property_ids[1], "title": "Gas Safety Certificate", "category": "gas_safety", 
         "expiry_date": (now + timedelta(days=200)).date().isoformat(),
         "notes": "Local Gas Safe engineer - expires August"},
        {"property_id": property_ids[1], "title": "EICR Certificate", "category": "eicr", 
         "expiry_date": (now + timedelta(days=25)).date().isoformat(),
         "notes": "Due for renewal next month"},
        {"property_id": property_ids[1], "title": "Fire Risk Assessment", "category": "fire_risk_assessment", 
         "expiry_date": (now + timedelta(days=90)).date().isoformat(),
         "notes": "Smoke alarms and fire extinguisher checked"},
        {"property_id": property_ids[1], "title": "EPC Rating", "category": "epc", 
         "expiry_date": (now + timedelta(days=2500)).date().isoformat(),
         "notes": "Rating: B (85) - recently upgraded insulation"},
        
        # Property 3 - Edinburgh (Scotland-specific)
        {"property_id": property_ids[2], "title": "Gas Safety Certificate", "category": "gas_safety", 
         "expiry_date": (now + timedelta(days=15)).date().isoformat(),
         "notes": "Booked with Scottish Gas for next week"},
        {"property_id": property_ids[2], "title": "Short-Term Let Licence", "category": "licence", 
         "expiry_date": (now + timedelta(days=300)).date().isoformat(),
         "notes": "Edinburgh Council licence - 3 year term"},
        {"property_id": property_ids[2], "title": "EICR Certificate", "category": "eicr", 
         "expiry_date": (now - timedelta(days=30)).date().isoformat(),
         "notes": "URGENT: Electrical inspection overdue"},
        {"property_id": property_ids[2], "title": "Legionella Risk Assessment", "category": "legionella", 
         "expiry_date": (now + timedelta(days=180)).date().isoformat(),
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
