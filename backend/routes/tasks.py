"""
Task routes for Staylet.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid

from models.database import db
from models.schemas import TaskCreate, TaskUpdate, TaskResponse
from utils.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    property_id: Optional[str] = None,
    task_status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    filter_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all tasks with optional filters."""
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


@router.get("/templates")
async def get_task_templates():
    """Get common task templates for quick creation."""
    return [
        {"title": "Smoke & CO Alarm Check", "category": "safety", "priority": "high", "description": "Test all smoke and carbon monoxide alarms", "is_recurring": True, "recurrence_pattern": "monthly"},
        {"title": "Insurance Renewal Follow-up", "category": "renewal", "priority": "high", "description": "Review and renew landlord insurance policy"},
        {"title": "Licence Renewal Application", "category": "renewal", "priority": "urgent", "description": "Submit property licence renewal application"},
        {"title": "Seasonal Property Check", "category": "seasonal", "priority": "medium", "description": "Inspect heating, ventilation, and weatherproofing", "is_recurring": True, "recurrence_pattern": "yearly"},
        {"title": "Guest Changeover Inspection", "category": "inspection", "priority": "medium", "description": "Verify property condition between guests"},
        {"title": "Fire Extinguisher Inspection", "category": "safety", "priority": "high", "description": "Check fire extinguisher pressure and expiry", "is_recurring": True, "recurrence_pattern": "yearly"},
        {"title": "Boiler Service", "category": "maintenance", "priority": "high", "description": "Annual boiler service and safety check", "is_recurring": True, "recurrence_pattern": "yearly"},
        {"title": "Deep Clean", "category": "maintenance", "priority": "medium", "description": "Professional deep cleaning of property", "is_recurring": True, "recurrence_pattern": "quarterly"}
    ]


@router.post("", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, current_user: dict = Depends(get_current_user)):
    """Create a new task."""
    # Validate property if specified
    if task_data.property_id:
        if not await db.properties.find_one({"id": task_data.property_id, "user_id": current_user["id"]}, {"_id": 0, "id": 1}):
            raise HTTPException(status_code=404, detail="Property not found")
    
    now = datetime.now(timezone.utc).isoformat()
    task_id = str(uuid.uuid4())
    task_doc = {
        "id": task_id,
        "user_id": current_user["id"],
        "property_id": task_data.property_id,
        "title": task_data.title,
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


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate, current_user: dict = Depends(get_current_user)):
    """Update an existing task."""
    task = await db.tasks.find_one({"id": task_id, "user_id": current_user["id"]}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = {k: v for k, v in task_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Handle recurring task completion
    if update_data.get("task_status") == "completed" and task.get("is_recurring") and task.get("recurrence_pattern"):
        # Create next occurrence
        pattern = task["recurrence_pattern"]
        current_due = task.get("due_date")
        if current_due:
            try:
                due_date = datetime.fromisoformat(current_due.replace('Z', '+00:00'))
                if pattern == "daily":
                    next_due = due_date + timedelta(days=1)
                elif pattern == "weekly":
                    next_due = due_date + timedelta(weeks=1)
                elif pattern == "monthly":
                    next_due = due_date + timedelta(days=30)
                elif pattern == "quarterly":
                    next_due = due_date + timedelta(days=90)
                elif pattern == "yearly":
                    next_due = due_date + timedelta(days=365)
                else:
                    next_due = due_date + timedelta(days=30)
                
                now = datetime.now(timezone.utc).isoformat()
                new_task_doc = {
                    "id": str(uuid.uuid4()),
                    "user_id": current_user["id"],
                    "property_id": task.get("property_id"),
                    "title": task["title"],
                    "description": task.get("description"),
                    "due_date": next_due.isoformat(),
                    "priority": task.get("priority", "medium"),
                    "task_status": "pending",
                    "category": task.get("category", "general"),
                    "is_recurring": True,
                    "recurrence_pattern": pattern,
                    "created_at": now,
                    "updated_at": now
                }
                await db.tasks.insert_one(new_task_doc)
            except (ValueError, TypeError):
                pass
    
    await db.tasks.update_one({"id": task_id, "user_id": current_user["id"]}, {"$set": update_data})
    return await db.tasks.find_one({"id": task_id, "user_id": current_user["id"]}, {"_id": 0})


@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a task."""
    result = await db.tasks.delete_one({"id": task_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
