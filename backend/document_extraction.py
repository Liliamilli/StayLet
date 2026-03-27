"""
Document Extraction Service using OpenAI GPT-4o Vision
Extracts document type, issue date, and expiry date from compliance certificates
"""
import os
import base64
import json
import re
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Try to import emergentintegrations
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    EMERGENT_AVAILABLE = True
except ImportError:
    EMERGENT_AVAILABLE = False
    print("Warning: emergentintegrations not available. Document extraction will be disabled.")

# Category mapping for document detection
CATEGORY_KEYWORDS = {
    "gas_safety": ["gas safety", "gas safe", "landlord gas safety", "cp12", "gas certificate", "boiler", "gas appliance"],
    "eicr": ["eicr", "electrical installation", "electrical condition", "electrical safety", "periodic inspection"],
    "epc": ["epc", "energy performance", "energy certificate", "energy rating", "domestic energy assessor"],
    "insurance": ["insurance", "landlord insurance", "property insurance", "buildings insurance", "public liability"],
    "fire_risk_assessment": ["fire risk", "fire safety", "fire assessment", "fire regulation"],
    "pat_testing": ["pat test", "portable appliance", "pat certificate", "electrical appliance test"],
    "legionella": ["legionella", "water safety", "water risk", "legionnaires"],
    "smoke_co_alarms": ["smoke alarm", "carbon monoxide", "co alarm", "smoke detector"],
    "licence": ["licence", "license", "hmo licence", "selective licence", "registration"],
}

CATEGORY_LABELS = {
    "gas_safety": "Gas Safety Certificate",
    "eicr": "EICR (Electrical Installation Condition Report)",
    "epc": "EPC (Energy Performance Certificate)",
    "insurance": "Insurance",
    "fire_risk_assessment": "Fire Risk Assessment",
    "pat_testing": "PAT Testing",
    "legionella": "Legionella Risk Assessment",
    "smoke_co_alarms": "Smoke/CO Alarms",
    "licence": "Licence/Registration",
    "custom": "Custom Document"
}

async def extract_document_info(file_base64: str, filename: str, mime_type: str) -> Dict[str, Any]:
    """
    Extract document information using GPT-4o vision.
    Returns extracted values with confidence levels.
    """
    if not EMERGENT_AVAILABLE:
        return {
            "success": False,
            "error": "Document extraction service not available",
            "extracted": {}
        }
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "API key not configured",
            "extracted": {}
        }
    
    try:
        # Initialize LLM chat
        chat = LlmChat(
            api_key=api_key,
            session_id=f"doc-extract-{datetime.now().timestamp()}",
            system_message="""You are a document analysis assistant specialized in UK property compliance certificates.
Your task is to extract key information from uploaded documents.

For each document, try to identify:
1. Document type (Gas Safety Certificate, EICR, EPC, Insurance, Fire Risk Assessment, PAT Testing, Legionella Assessment, Smoke/CO Alarms certificate, Licence, or Custom)
2. Issue date (when the certificate was issued)
3. Expiry date (when the certificate expires)
4. Any certificate reference number

Be conservative in your confidence levels:
- HIGH: Information is clearly visible and unambiguous
- MEDIUM: Information is present but may require interpretation
- LOW: Information is inferred or partially visible
- NOT_FOUND: Information could not be extracted

Always respond in valid JSON format."""
        ).with_model("openai", "gpt-4o")
        
        # Create the analysis prompt
        prompt = f"""Analyze this document (filename: {filename}).

Extract the following information and respond in this exact JSON format:
{{
    "document_type": {{
        "value": "gas_safety|eicr|epc|insurance|fire_risk_assessment|pat_testing|legionella|smoke_co_alarms|licence|custom",
        "label": "Human readable document type name",
        "confidence": "HIGH|MEDIUM|LOW"
    }},
    "issue_date": {{
        "value": "YYYY-MM-DD or null if not found",
        "raw_text": "The date as it appears in the document",
        "confidence": "HIGH|MEDIUM|LOW|NOT_FOUND"
    }},
    "expiry_date": {{
        "value": "YYYY-MM-DD or null if not found", 
        "raw_text": "The date as it appears in the document",
        "confidence": "HIGH|MEDIUM|LOW|NOT_FOUND"
    }},
    "certificate_number": {{
        "value": "Reference number if found, null otherwise",
        "confidence": "HIGH|MEDIUM|LOW|NOT_FOUND"
    }},
    "property_address": {{
        "value": "Property address if visible, null otherwise",
        "confidence": "HIGH|MEDIUM|LOW|NOT_FOUND"  
    }},
    "notes": "Any additional relevant information about the document"
}}

Important:
- Dates should be in YYYY-MM-DD format
- For UK documents, dates are often in DD/MM/YYYY format - convert them correctly
- Gas Safety Certificates are valid for 12 months from issue date
- EICRs are typically valid for 5 years
- EPCs are valid for 10 years
- If you can see the issue date but not expiry, you can infer the expiry based on document type
- Mark inferred values as MEDIUM confidence

Only respond with the JSON object, no other text."""

        # Create image content for the message
        image_content = ImageContent(image_base64=file_base64)
        
        user_message = UserMessage(
            text=prompt,
            image_contents=[image_content]
        )
        
        # Send message and get response
        response = await chat.send_message(user_message)
        
        # Parse the JSON response
        try:
            # Clean up the response - remove markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith("```"):
                # Remove markdown code block
                clean_response = re.sub(r'^```(?:json)?\n?', '', clean_response)
                clean_response = re.sub(r'\n?```$', '', clean_response)
            
            extracted_data = json.loads(clean_response)
            
            return {
                "success": True,
                "extracted": extracted_data,
                "error": None
            }
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract what we can
            return {
                "success": False,
                "error": f"Failed to parse extraction response: {str(e)}",
                "raw_response": response,
                "extracted": {}
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Extraction failed: {str(e)}",
            "extracted": {}
        }


def suggest_category_from_filename(filename: str) -> Optional[str]:
    """
    Suggest a compliance category based on filename keywords.
    Returns category key or None if no match found.
    """
    filename_lower = filename.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in filename_lower:
                return category
    
    return None


def format_extracted_for_ui(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format extraction results for the frontend UI.
    Returns a simplified structure with values and confidence indicators.
    """
    if not extraction_result.get("success"):
        return {
            "success": False,
            "error": extraction_result.get("error", "Unknown error"),
            "suggestions": {}
        }
    
    extracted = extraction_result.get("extracted", {})
    
    suggestions = {
        "category": None,
        "title": None,
        "issue_date": None,
        "expiry_date": None,
        "notes": None,
        "confidence_summary": "LOW"
    }
    
    # Document type -> category
    doc_type = extracted.get("document_type", {})
    if doc_type.get("value"):
        suggestions["category"] = {
            "value": doc_type["value"],
            "label": doc_type.get("label", CATEGORY_LABELS.get(doc_type["value"], "Unknown")),
            "confidence": doc_type.get("confidence", "LOW"),
            "is_suggested": True
        }
        # Use document type as title
        suggestions["title"] = {
            "value": doc_type.get("label", CATEGORY_LABELS.get(doc_type["value"], "Document")),
            "confidence": doc_type.get("confidence", "LOW"),
            "is_suggested": True
        }
    
    # Issue date
    issue_date = extracted.get("issue_date", {})
    if issue_date.get("value"):
        suggestions["issue_date"] = {
            "value": issue_date["value"],
            "raw_text": issue_date.get("raw_text"),
            "confidence": issue_date.get("confidence", "LOW"),
            "is_suggested": True
        }
    
    # Expiry date
    expiry_date = extracted.get("expiry_date", {})
    if expiry_date.get("value"):
        suggestions["expiry_date"] = {
            "value": expiry_date["value"],
            "raw_text": expiry_date.get("raw_text"),
            "confidence": expiry_date.get("confidence", "LOW"),
            "is_suggested": True
        }
    
    # Notes from certificate number and additional info
    notes_parts = []
    cert_num = extracted.get("certificate_number", {})
    if cert_num.get("value"):
        notes_parts.append(f"Certificate: {cert_num['value']}")
    
    address = extracted.get("property_address", {})
    if address.get("value"):
        notes_parts.append(f"Property: {address['value']}")
    
    if extracted.get("notes"):
        notes_parts.append(extracted["notes"])
    
    if notes_parts:
        suggestions["notes"] = {
            "value": " | ".join(notes_parts),
            "confidence": "MEDIUM",
            "is_suggested": True
        }
    
    # Calculate overall confidence
    confidences = []
    for key in ["category", "issue_date", "expiry_date"]:
        if suggestions[key] and suggestions[key].get("confidence"):
            confidences.append(suggestions[key]["confidence"])
    
    if "HIGH" in confidences and confidences.count("HIGH") >= 2:
        suggestions["confidence_summary"] = "HIGH"
    elif "MEDIUM" in confidences or "HIGH" in confidences:
        suggestions["confidence_summary"] = "MEDIUM"
    else:
        suggestions["confidence_summary"] = "LOW"
    
    return {
        "success": True,
        "suggestions": suggestions,
        "error": None
    }
