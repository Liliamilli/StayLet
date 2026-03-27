"""
AI Assistant for Staylet - Provides data-grounded insights and natural language queries.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Category labels for human-readable output
CATEGORY_LABELS = {
    'gas_safety': 'Gas Safety Certificate',
    'eicr': 'EICR',
    'epc': 'EPC',
    'insurance': 'Insurance',
    'fire_risk_assessment': 'Fire Risk Assessment',
    'pat_testing': 'PAT Testing',
    'legionella': 'Legionella Risk Assessment',
    'smoke_co_alarms': 'Smoke/CO Alarms',
    'licence': 'Licence',
    'custom': 'Custom'
}

# Required compliance categories for UK short-lets
REQUIRED_CATEGORIES = ['gas_safety', 'eicr', 'epc', 'insurance', 'smoke_co_alarms']


def days_until(date_str: str) -> Optional[int]:
    """Calculate days until a date."""
    if not date_str:
        return None
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        return (dt.date() - datetime.now(timezone.utc).date()).days
    except (ValueError, TypeError):
        return None


def get_category_label(category: str) -> str:
    """Get human-readable category label."""
    return CATEGORY_LABELS.get(category, category.replace('_', ' ').title())


async def get_structured_insights(db, user_id: str) -> Dict[str, Any]:
    """
    Generate structured insights from user data.
    This is the fast, pure-data approach - no LLM needed.
    """
    now = datetime.now(timezone.utc)
    today = now.date()
    month_end = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    # Fetch all user data
    properties = await db.properties.find(
        {"user_id": user_id, "property_status": "active"},
        {"_id": 0}
    ).to_list(100)
    
    compliance_records = await db.compliance_records.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(500)
    
    tasks = await db.tasks.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(500)
    
    # Build property lookup
    property_map = {p["id"]: p for p in properties}
    
    # Analyze compliance by property
    property_compliance = {}
    for prop in properties:
        property_compliance[prop["id"]] = {
            "property": prop,
            "records": [],
            "missing_categories": list(REQUIRED_CATEGORIES),
            "overdue": [],
            "expiring_soon": [],
            "compliant": []
        }
    
    for record in compliance_records:
        prop_id = record.get("property_id")
        if prop_id not in property_compliance:
            continue
        
        pc = property_compliance[prop_id]
        pc["records"].append(record)
        
        # Remove from missing if present
        cat = record.get("category")
        if cat in pc["missing_categories"]:
            pc["missing_categories"].remove(cat)
        
        # Categorize by status
        status = record.get("compliance_status", "compliant")
        if status == "overdue":
            pc["overdue"].append(record)
        elif status == "expiring_soon":
            pc["expiring_soon"].append(record)
        else:
            pc["compliant"].append(record)
    
    # Calculate risk scores
    property_risks = []
    for prop_id, pc in property_compliance.items():
        risk_score = 0
        risk_reasons = []
        
        # Overdue items are highest risk
        if pc["overdue"]:
            risk_score += len(pc["overdue"]) * 30
            risk_reasons.append(f"{len(pc['overdue'])} overdue")
        
        # Missing required categories
        if pc["missing_categories"]:
            risk_score += len(pc["missing_categories"]) * 20
            risk_reasons.append(f"{len(pc['missing_categories'])} missing")
        
        # Expiring soon
        if pc["expiring_soon"]:
            risk_score += len(pc["expiring_soon"]) * 10
            risk_reasons.append(f"{len(pc['expiring_soon'])} expiring soon")
        
        property_risks.append({
            "property_id": prop_id,
            "property_name": pc["property"].get("name", "Unknown"),
            "risk_score": risk_score,
            "risk_reasons": risk_reasons,
            "overdue_count": len(pc["overdue"]),
            "expiring_count": len(pc["expiring_soon"]),
            "missing_count": len(pc["missing_categories"]),
            "missing_categories": pc["missing_categories"]
        })
    
    # Sort by risk score
    property_risks.sort(key=lambda x: x["risk_score"], reverse=True)
    
    # Find items expiring this month
    expiring_this_month = []
    for record in compliance_records:
        expiry = record.get("expiry_date")
        days = days_until(expiry)
        if days is not None and 0 <= days <= (month_end.day - today.day + 1):
            prop = property_map.get(record.get("property_id"), {})
            expiring_this_month.append({
                "record_id": record.get("id"),
                "title": record.get("title"),
                "category": get_category_label(record.get("category", "")),
                "expiry_date": expiry,
                "days_until": days,
                "property_id": record.get("property_id"),
                "property_name": prop.get("name", "Unknown")
            })
    expiring_this_month.sort(key=lambda x: x["days_until"])
    
    # Tasks needing attention this month
    tasks_this_month = []
    for task in tasks:
        if task.get("task_status") == "completed":
            continue
        due_date = task.get("due_date")
        days = days_until(due_date)
        if days is not None and days <= (month_end.day - today.day + 1):
            prop = property_map.get(task.get("property_id"), {})
            tasks_this_month.append({
                "task_id": task.get("id"),
                "title": task.get("title"),
                "due_date": due_date,
                "days_until": days,
                "priority": task.get("priority", "medium"),
                "status": task.get("task_status", "pending"),
                "property_id": task.get("property_id"),
                "property_name": prop.get("name", "Unknown") if task.get("property_id") else "General"
            })
    tasks_this_month.sort(key=lambda x: (x["days_until"], {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 2)))
    
    # Build urgent actions list
    urgent_actions = []
    
    # Add overdue items first
    for record in compliance_records:
        if record.get("compliance_status") == "overdue":
            prop = property_map.get(record.get("property_id"), {})
            urgent_actions.append({
                "type": "overdue",
                "priority": "critical",
                "action": f"Renew {get_category_label(record.get('category', ''))}",
                "detail": record.get("title"),
                "property_name": prop.get("name", "Unknown"),
                "property_id": record.get("property_id"),
                "record_id": record.get("id"),
                "days_overdue": abs(days_until(record.get("expiry_date")) or 0)
            })
    
    # Add tasks that are overdue or urgent
    for task in tasks:
        if task.get("task_status") == "completed":
            continue
        days = days_until(task.get("due_date"))
        if days is not None and days < 0:
            prop = property_map.get(task.get("property_id"), {})
            urgent_actions.append({
                "type": "overdue_task",
                "priority": "high",
                "action": f"Complete task: {task.get('title')}",
                "detail": f"Overdue by {abs(days)} days",
                "property_name": prop.get("name", "General") if task.get("property_id") else "General",
                "property_id": task.get("property_id"),
                "task_id": task.get("id")
            })
    
    # Sort urgent actions
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    urgent_actions.sort(key=lambda x: priority_order.get(x["priority"], 2))
    
    # Build missing compliance by property summary
    missing_by_property = []
    for pr in property_risks:
        if pr["missing_categories"]:
            missing_by_property.append({
                "property_id": pr["property_id"],
                "property_name": pr["property_name"],
                "missing": [get_category_label(c) for c in pr["missing_categories"]]
            })
    
    return {
        "summary": {
            "total_properties": len(properties),
            "total_records": len(compliance_records),
            "total_tasks": len(tasks),
            "overdue_records": sum(1 for r in compliance_records if r.get("compliance_status") == "overdue"),
            "expiring_soon_records": sum(1 for r in compliance_records if r.get("compliance_status") == "expiring_soon"),
            "pending_tasks": sum(1 for t in tasks if t.get("task_status") != "completed")
        },
        "highest_risk_property": property_risks[0] if property_risks and property_risks[0]["risk_score"] > 0 else None,
        "property_risks": property_risks[:5],  # Top 5 at-risk properties
        "urgent_actions": urgent_actions[:5],  # Top 5 urgent actions
        "expiring_this_month": expiring_this_month[:10],
        "tasks_this_month": tasks_this_month[:10],
        "missing_by_property": missing_by_property
    }


async def get_property_insights(db, user_id: str, property_id: str) -> Dict[str, Any]:
    """
    Get AI insights for a specific property.
    """
    # Fetch property
    property_data = await db.properties.find_one(
        {"id": property_id, "user_id": user_id},
        {"_id": 0}
    )
    if not property_data:
        return {"error": "Property not found"}
    
    # Fetch compliance records for this property
    records = await db.compliance_records.find(
        {"property_id": property_id, "user_id": user_id},
        {"_id": 0}
    ).to_list(100)
    
    # Fetch tasks for this property
    tasks = await db.tasks.find(
        {"property_id": property_id, "user_id": user_id},
        {"_id": 0}
    ).to_list(100)
    
    # Analyze
    missing_categories = list(REQUIRED_CATEGORIES)
    overdue_records = []
    expiring_soon_records = []
    compliant_records = []
    
    for record in records:
        cat = record.get("category")
        if cat in missing_categories:
            missing_categories.remove(cat)
        
        status = record.get("compliance_status", "compliant")
        record_info = {
            "id": record.get("id"),
            "title": record.get("title"),
            "category": get_category_label(record.get("category", "")),
            "expiry_date": record.get("expiry_date"),
            "days_until": days_until(record.get("expiry_date"))
        }
        
        if status == "overdue":
            overdue_records.append(record_info)
        elif status == "expiring_soon":
            expiring_soon_records.append(record_info)
        else:
            compliant_records.append(record_info)
    
    # Pending tasks
    pending_tasks = []
    for task in tasks:
        if task.get("task_status") == "completed":
            continue
        pending_tasks.append({
            "id": task.get("id"),
            "title": task.get("title"),
            "due_date": task.get("due_date"),
            "days_until": days_until(task.get("due_date")),
            "priority": task.get("priority", "medium")
        })
    pending_tasks.sort(key=lambda x: (x["days_until"] or 999, {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 2)))
    
    # Build recommended actions
    recommended_actions = []
    
    for record in overdue_records:
        recommended_actions.append({
            "priority": "critical",
            "action": f"Renew {record['category']} immediately",
            "detail": f"{record['title']} is {abs(record['days_until'] or 0)} days overdue",
            "record_id": record["id"]
        })
    
    for cat in missing_categories:
        recommended_actions.append({
            "priority": "high",
            "action": f"Add {get_category_label(cat)}",
            "detail": "Required for UK short-let compliance",
            "category": cat
        })
    
    for record in expiring_soon_records[:3]:
        recommended_actions.append({
            "priority": "medium",
            "action": f"Schedule renewal for {record['category']}",
            "detail": f"Expires in {record['days_until']} days",
            "record_id": record["id"]
        })
    
    # Calculate compliance score
    total_required = len(REQUIRED_CATEGORIES)
    compliant_count = total_required - len(missing_categories) - len([r for r in overdue_records if r.get("category") in REQUIRED_CATEGORIES])
    compliance_score = int((compliant_count / total_required) * 100) if total_required > 0 else 100
    
    return {
        "property": {
            "id": property_data.get("id"),
            "name": property_data.get("name"),
            "address": property_data.get("address"),
            "postcode": property_data.get("postcode")
        },
        "compliance_score": compliance_score,
        "missing_records": [get_category_label(c) for c in missing_categories],
        "overdue_records": overdue_records,
        "expiring_soon_records": expiring_soon_records,
        "compliant_records": compliant_records,
        "pending_tasks": pending_tasks[:5],
        "recommended_actions": recommended_actions[:5],
        "summary": {
            "total_records": len(records),
            "compliant": len(compliant_records),
            "expiring_soon": len(expiring_soon_records),
            "overdue": len(overdue_records),
            "missing": len(missing_categories),
            "pending_tasks": len(pending_tasks)
        }
    }


async def answer_natural_language_query(db, user_id: str, question: str) -> Dict[str, Any]:
    """
    Answer a natural language question using LLM with user's actual data.
    """
    # Get structured insights first
    insights = await get_structured_insights(db, user_id)
    
    # Build context from actual data
    context_parts = []
    
    # Summary
    s = insights["summary"]
    context_parts.append(f"User has {s['total_properties']} properties with {s['total_records']} compliance records and {s['total_tasks']} tasks.")
    context_parts.append(f"Status: {s['overdue_records']} overdue, {s['expiring_soon_records']} expiring soon, {s['pending_tasks']} pending tasks.")
    
    # Highest risk
    if insights["highest_risk_property"]:
        hr = insights["highest_risk_property"]
        context_parts.append(f"Highest risk property: {hr['property_name']} - {', '.join(hr['risk_reasons'])}.")
    
    # Expiring this month
    if insights["expiring_this_month"]:
        exp_list = [f"{e['title']} at {e['property_name']} (in {e['days_until']} days)" for e in insights["expiring_this_month"][:5]]
        context_parts.append(f"Expiring this month: {'; '.join(exp_list)}.")
    
    # Missing compliance
    if insights["missing_by_property"]:
        missing_list = [f"{m['property_name']}: {', '.join(m['missing'])}" for m in insights["missing_by_property"][:3]]
        context_parts.append(f"Missing compliance: {'; '.join(missing_list)}.")
    
    # Urgent actions
    if insights["urgent_actions"]:
        urgent_list = [f"{a['action']} ({a['property_name']})" for a in insights["urgent_actions"][:3]]
        context_parts.append(f"Urgent actions: {'; '.join(urgent_list)}.")
    
    # Tasks this month
    if insights["tasks_this_month"]:
        task_list = [f"{t['title']} - {t['property_name']} (in {t['days_until']} days)" for t in insights["tasks_this_month"][:5]]
        context_parts.append(f"Tasks this month: {'; '.join(task_list)}.")
    
    context = "\n".join(context_parts)
    
    # Initialize LLM
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return {
            "answer": "I can help with your compliance questions, but the AI service is not configured. Please check your settings.",
            "source": "error",
            "data": None
        }
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"assistant-{user_id}-{datetime.now().timestamp()}",
        system_message="""You are Staylet's compliance assistant for UK short-term let hosts.

RULES:
1. Answer ONLY based on the data provided. Never make up information.
2. Be concise and direct. No fluff or unnecessary words.
3. When mentioning items, be specific with names and dates.
4. If asked about something not in the data, say "I don't have that information in your current data."
5. Format responses clearly - use bullet points for lists.
6. Focus on actionable insights.
7. Never give generic compliance advice - only reference what's in the user's actual data."""
    ).with_model("openai", "gpt-4o")
    
    # Send the question with context
    user_message = UserMessage(
        text=f"""User's compliance data:
{context}

User question: {question}

Answer based ONLY on the data above. Be specific and concise."""
    )
    
    try:
        response = await chat.send_message(user_message)
        return {
            "answer": response,
            "source": "llm",
            "data": insights
        }
    except Exception as e:
        return {
            "answer": f"Sorry, I couldn't process your question. Error: {str(e)}",
            "source": "error",
            "data": insights
        }
