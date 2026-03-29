"""
Compliance record routes for Staylet.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from models.database import db
from models.schemas import ComplianceRecordCreate, ComplianceRecordUpdate, ComplianceRecordResponse, BulkComplianceCreate
from utils.auth import get_current_user, calculate_compliance_status

router = APIRouter(prefix="/compliance-records", tags=["Compliance"])


@router.get("", response_model=List[ComplianceRecordResponse])
async def get_compliance_records(
    property_id: Optional[str] = None,
    category: Optional[str] = None,
    compliance_status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all compliance records with optional filters."""
    query = {"user_id": current_user["id"]}
    if property_id:
        query["property_id"] = property_id
    if category:
        query["category"] = category
    if compliance_status:
        query["compliance_status"] = compliance_status
    return await db.compliance_records.find(query, {"_id": 0}).to_list(500)


@router.get("/{record_id}", response_model=ComplianceRecordResponse)
async def get_compliance_record(record_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific compliance record."""
    record = await db.compliance_records.find_one(
        {"id": record_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not record:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    return record


@router.post("", response_model=ComplianceRecordResponse)
async def create_compliance_record(record_data: ComplianceRecordCreate, current_user: dict = Depends(get_current_user)):
    """Create a new compliance record."""
    # Validate required fields
    if not record_data.title or not record_data.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    if not record_data.category or not record_data.category.strip():
        raise HTTPException(status_code=400, detail="Category is required")
    if not record_data.property_id or not record_data.property_id.strip():
        raise HTTPException(status_code=400, detail="Property ID is required")
    
    # Verify property exists
    if not await db.properties.find_one({"id": record_data.property_id, "user_id": current_user["id"]}, {"_id": 0, "id": 1}):
        raise HTTPException(status_code=404, detail="Property not found")
    
    now = datetime.now(timezone.utc).isoformat()
    record_id = str(uuid.uuid4())
    record_doc = {
        "id": record_id,
        "user_id": current_user["id"],
        "property_id": record_data.property_id,
        "title": record_data.title.strip(),
        "category": record_data.category.strip(),
        "compliance_status": calculate_compliance_status(record_data.expiry_date, True),
        "issue_date": record_data.issue_date,
        "expiry_date": record_data.expiry_date,
        "reminder_preference": record_data.reminder_preference,
        "notes": record_data.notes,
        "created_at": now,
        "updated_at": now
    }
    await db.compliance_records.insert_one(record_doc)
    return record_doc


@router.put("/{record_id}", response_model=ComplianceRecordResponse)
async def update_compliance_record(record_id: str, record_data: ComplianceRecordUpdate, current_user: dict = Depends(get_current_user)):
    """Update an existing compliance record."""
    if not await db.compliance_records.find_one({"id": record_id, "user_id": current_user["id"]}, {"_id": 0}):
        raise HTTPException(status_code=404, detail="Compliance record not found")
    
    update_data = {k: v for k, v in record_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    if "expiry_date" in update_data:
        update_data["compliance_status"] = calculate_compliance_status(update_data["expiry_date"], True)
    
    await db.compliance_records.update_one(
        {"id": record_id, "user_id": current_user["id"]},
        {"$set": update_data}
    )
    return await db.compliance_records.find_one({"id": record_id, "user_id": current_user["id"]}, {"_id": 0})


@router.delete("/{record_id}")
async def delete_compliance_record(record_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a compliance record."""
    result = await db.compliance_records.delete_one({"id": record_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    return {"message": "Compliance record deleted successfully"}


@router.get("/{record_id}/documents")
async def get_record_documents(record_id: str, current_user: dict = Depends(get_current_user)):
    """Get documents linked to a compliance record."""
    # Verify record exists
    record = await db.compliance_records.find_one(
        {"id": record_id, "user_id": current_user["id"]},
        {"_id": 0, "id": 1}
    )
    if not record:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    
    documents = await db.documents.find(
        {"compliance_record_id": record_id, "user_id": current_user["id"]},
        {"_id": 0}
    ).to_list(100)
    return documents
