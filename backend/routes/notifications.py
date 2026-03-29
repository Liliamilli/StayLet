"""
Notification routes for Staylet.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, timezone
import uuid

from models.database import db
from models.schemas import NotificationResponse, UserPreferencesUpdate, UserPreferencesResponse, ContactFormRequest
from utils.auth import get_current_user

router = APIRouter(tags=["Notifications"])


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(unread_only: bool = False, current_user: dict = Depends(get_current_user)):
    """Get user notifications."""
    query = {"user_id": current_user["id"]}
    if unread_only:
        query["is_read"] = False
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
    return notifications


@router.get("/notifications/generate")
async def generate_notifications(current_user: dict = Depends(get_current_user)):
    """Generate notifications based on compliance records and tasks."""
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
            
            for lead_days in reminder_days:
                if days_until == lead_days or (days_until < 0 and lead_days == 0):
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


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a notification as read."""
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"is_read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@router.put("/notifications/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read."""
    await db.notifications.update_many(
        {"user_id": current_user["id"], "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"message": "All notifications marked as read"}


@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a notification."""
    result = await db.notifications.delete_one({"id": notification_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}


# User Preferences
@router.get("/user/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(current_user: dict = Depends(get_current_user)):
    """Get user preferences."""
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


@router.put("/user/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(prefs_data: UserPreferencesUpdate, current_user: dict = Depends(get_current_user)):
    """Update user preferences."""
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


@router.post("/contact")
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
    await db.contacts.insert_one(contact_doc)
    return {"success": True, "message": "Your message has been received. We'll get back to you soon."}
