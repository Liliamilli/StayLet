"""
Property routes for Staylet.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from models.database import db
from models.schemas import PropertyCreate, PropertyUpdate, PropertyResponse
from utils.auth import get_current_user
from utils.constants import SUBSCRIPTION_PLANS
from pdf_generator import generate_compliance_report

router = APIRouter(prefix="/properties", tags=["Properties"])


async def get_property_compliance_summary(property_id: str, user_id: str) -> dict:
    """Calculate compliance summary for a property."""
    records = await db.compliance_records.find(
        {"property_id": property_id, "user_id": user_id},
        {"_id": 0, "compliance_status": 1}
    ).to_list(100)
    
    summary = {"total": len(records), "compliant": 0, "expiring_soon": 0, "overdue": 0, "missing": 0}
    for record in records:
        status = record.get("compliance_status", "compliant")
        if status in summary:
            summary[status] += 1
    return summary


@router.get("", response_model=List[PropertyResponse])
async def get_properties(search: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Get all properties for the current user."""
    query = {"user_id": current_user["id"]}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"address": {"$regex": search, "$options": "i"}},
            {"postcode": {"$regex": search, "$options": "i"}}
        ]
    properties = await db.properties.find(query, {"_id": 0}).to_list(100)
    for prop in properties:
        prop["compliance_summary"] = await get_property_compliance_summary(prop["id"], current_user["id"])
    return properties


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific property by ID."""
    prop = await db.properties.find_one(
        {"id": property_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    prop["compliance_summary"] = await get_property_compliance_summary(property_id, current_user["id"])
    return prop


@router.post("", response_model=PropertyResponse)
async def create_property(property_data: PropertyCreate, current_user: dict = Depends(get_current_user)):
    """Create a new property."""
    # Check plan limit before creating property
    plan = current_user.get("subscription_plan", "solo")
    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["solo"])
    property_limit = plan_info["property_limit"]
    
    current_count = await db.properties.count_documents({
        "user_id": current_user["id"],
        "property_status": "active"
    })
    
    if current_count >= property_limit:
        raise HTTPException(
            status_code=403, 
            detail=f"Property limit reached. Your {plan_info['name']} plan allows {property_limit} {'property' if property_limit == 1 else 'properties'}. Please upgrade to add more."
        )
    
    # Validate required fields are not empty
    if not property_data.name or not property_data.name.strip():
        raise HTTPException(status_code=400, detail="Property name is required")
    if not property_data.address or not property_data.address.strip():
        raise HTTPException(status_code=400, detail="Address is required")
    if not property_data.postcode or not property_data.postcode.strip():
        raise HTTPException(status_code=400, detail="Postcode is required")
    
    now = datetime.now(timezone.utc).isoformat()
    property_id = str(uuid.uuid4())
    property_doc = {
        "id": property_id,
        "user_id": current_user["id"],
        "name": property_data.name.strip(),
        "address": property_data.address.strip(),
        "postcode": property_data.postcode.strip().upper(),
        "uk_nation": property_data.uk_nation,
        "is_in_london": property_data.is_in_london,
        "property_type": property_data.property_type,
        "ownership_type": property_data.ownership_type,
        "bedrooms": property_data.bedrooms,
        "notes": property_data.notes,
        "property_status": "active",
        "created_at": now,
        "updated_at": now
    }
    await db.properties.insert_one(property_doc)
    property_doc["compliance_summary"] = {"total": 0, "compliant": 0, "expiring_soon": 0, "overdue": 0, "missing": 0}
    return property_doc


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(property_id: str, property_data: PropertyUpdate, current_user: dict = Depends(get_current_user)):
    """Update an existing property."""
    if not await db.properties.find_one({"id": property_id, "user_id": current_user["id"]}, {"_id": 0}):
        raise HTTPException(status_code=404, detail="Property not found")
    
    update_data = {k: v for k, v in property_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    if "postcode" in update_data:
        update_data["postcode"] = update_data["postcode"].upper()
    
    await db.properties.update_one(
        {"id": property_id, "user_id": current_user["id"]},
        {"$set": update_data}
    )
    updated = await db.properties.find_one({"id": property_id, "user_id": current_user["id"]}, {"_id": 0})
    updated["compliance_summary"] = await get_property_compliance_summary(property_id, current_user["id"])
    return updated


@router.delete("/{property_id}")
async def delete_property(property_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a property and its associated records."""
    result = await db.properties.delete_one({"id": property_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Delete associated records
    await db.compliance_records.delete_many({"property_id": property_id, "user_id": current_user["id"]})
    await db.tasks.delete_many({"property_id": property_id, "user_id": current_user["id"]})
    return {"message": "Property deleted successfully"}


@router.get("/{property_id}/export")
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
