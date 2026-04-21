"""Map structured requirements to Salesforce objects, fields, and flows."""
import json
from typing import Any, Dict, List, Optional

from app.ai_engine import call_llm


# Configurable mapping rules for Sales Cloud
SALESFORCE_MAPPING_RULES = {
    "objects": {
        "customer": ["Account", "Contact"],
        "lead": ["Lead"],
        "opportunity": ["Opportunity"],
        "deal": ["Opportunity", "Quote"],
        "project": ["Project__c", "Task"],
        "contract": ["Contract"],
        "invoice": ["Invoice__c"],
        "product": ["Product2"],
        "campaign": ["Campaign"],
        "case": ["Case"],
    },
    "fields": {
        "name": "Name",
        "email": "Email",
        "phone": "Phone",
        "address": "BillingAddress",
        "amount": "Amount",
        "stage": "StageName",
        "status": "Status",
        "priority": "Priority",
        "description": "Description",
        "date": "CloseDate",
        "owner": "OwnerId",
    },
    "flows": {
        "lead_conversion": "Lead Conversion Flow",
        "opportunity_management": "Opportunity Management Flow",
        "approval_process": "Approval Process Flow",
        "data_sync": "Data Synchronization Flow",
        "notification": "Notification Flow",
        "validation": "Validation Flow",
    }
}


def _validate_salesforce_mapping(data: Any) -> bool:
    """Validate that Salesforce mapping matches expected schema."""
    if not isinstance(data, dict):
        return False

    required_keys = {"objects", "fields", "flows"}
    if not required_keys.issubset(data.keys()):
        return False

    # Validate objects
    if not isinstance(data["objects"], list):
        return False
    if not all(isinstance(obj, str) for obj in data["objects"]):
        return False

    # Validate fields
    if not isinstance(data["fields"], dict):
        return False
    for field_name, field_mapping in data["fields"].items():
        if not isinstance(field_name, str) or not isinstance(field_mapping, str):
            return False

    # Validate flows
    if not isinstance(data["flows"], list):
        return False
    if not all(isinstance(flow, str) for flow in data["flows"]):
        return False

    return True


def _sanitize_salesforce_mapping(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and normalize Salesforce mapping data."""
    sanitized = {
        "objects": [],
        "fields": {},
        "flows": []
    }

    # Sanitize objects
    objects = data.get("objects", [])
    if isinstance(objects, list):
        sanitized["objects"] = [str(obj).strip() for obj in objects if obj and str(obj).strip()]

    # Sanitize fields
    fields = data.get("fields", {})
    if isinstance(fields, dict):
        sanitized["fields"] = {
            str(k).strip(): str(v).strip()
            for k, v in fields.items()
            if k and v and str(k).strip() and str(v).strip()
        }

    # Sanitize flows
    flows = data.get("flows", [])
    if isinstance(flows, list):
        sanitized["flows"] = [str(flow).strip() for flow in flows if flow and str(flow).strip()]

    return sanitized


def _build_salesforce_prompt(requirements: List[str], pain_points: List[str]) -> str:
    """Build a prompt for Salesforce mapping using requirements and pain points."""
    requirements_text = "\n".join(f"- {req}" for req in requirements)
    pain_points_text = "\n".join(f"- {pp}" for pp in pain_points)

    return f"""You are a Salesforce Sales Cloud expert. Analyze the following requirements and pain points, then map them to appropriate Salesforce objects, fields, and flows.

REQUIREMENTS:
{requirements_text}

PAIN POINTS:
{pain_points_text}

Based on Sales Cloud best practices, provide a mapping that includes:

1. OBJECTS: Standard and custom Salesforce objects needed (e.g., Account, Opportunity, Lead, custom objects)
2. FIELDS: Key fields that should be created or used on these objects
3. FLOWS: Process automation flows, approval processes, or record-triggered flows needed

Return ONLY valid JSON with this structure:
{{
  "objects": ["Object1", "Object2", "Custom_Object__c"],
  "fields": {{
    "field_key": "Salesforce_Field_API_Name",
    "another_field": "Another_Field__c"
  }},
  "flows": ["Flow Name 1", "Flow Name 2"]
}}

Focus on Sales Cloud use cases like lead management, opportunity tracking, account management, and sales processes."""


def map_requirements_to_salesforce(
    requirements: List[str],
    pain_points: Optional[List[str]] = None,
    context_chunks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Map requirements to Salesforce objects, fields, and flows using AI."""
    if not requirements:
        return {
            "objects": [],
            "fields": {},
            "flows": []
        }

    pain_points = pain_points or []
    context_chunks = context_chunks or []

    prompt = _build_salesforce_prompt(requirements, pain_points)

    # Add context if available
    if context_chunks:
        context_text = "\n".join(f"Context: {chunk}" for chunk in context_chunks[:3])
        prompt += f"\n\nADDITIONAL CONTEXT:\n{context_text}"

    response = call_llm(prompt, response_format="json")

    if not response:
        return _fallback_salesforce_mapping(requirements, pain_points)

    try:
        # Parse JSON response
        if isinstance(response, str):
            parsed = json.loads(response)
        else:
            parsed = response

        # Validate and sanitize
        if _validate_salesforce_mapping(parsed):
            return _sanitize_salesforce_mapping(parsed)
        else:
            print("[SALESFORCE MAPPER] Invalid response format, using fallback")
            return _fallback_salesforce_mapping(requirements, pain_points)

    except (json.JSONDecodeError, TypeError) as e:
        print(f"[SALESFORCE MAPPER] JSON parsing error: {e}, using fallback")
        return _fallback_salesforce_mapping(requirements, pain_points)


def _fallback_salesforce_mapping(requirements: List[str], pain_points: List[str]) -> Dict[str, Any]:
    """Fallback Salesforce mapping when AI fails."""
    objects = []
    fields = {}
    flows = []

    # Simple keyword-based mapping
    req_text = " ".join(requirements).lower()
    pp_text = " ".join(pain_points).lower()
    combined_text = req_text + " " + pp_text

    # Object mapping based on keywords
    if any(word in combined_text for word in ["customer", "client", "account"]):
        objects.extend(["Account", "Contact"])
    if any(word in combined_text for word in ["lead", "prospect"]):
        objects.append("Lead")
    if any(word in combined_text for word in ["opportunity", "deal", "sale"]):
        objects.append("Opportunity")
    if any(word in combined_text for word in ["campaign", "marketing"]):
        objects.append("Campaign")
    if any(word in combined_text for word in ["case", "support", "issue"]):
        objects.append("Case")

    # Field mapping
    if "email" in combined_text:
        fields["email"] = "Email"
    if any(word in combined_text for word in ["phone", "call"]):
        fields["phone"] = "Phone"
    if any(word in combined_text for word in ["amount", "value", "price"]):
        fields["amount"] = "Amount"
    if any(word in combined_text for word in ["date", "deadline"]):
        fields["close_date"] = "CloseDate"
    if any(word in combined_text for word in ["status", "state"]):
        fields["status"] = "Status"
    if any(word in combined_text for word in ["priority", "urgent"]):
        fields["priority"] = "Priority"

    # Flow mapping
    if any(word in combined_text for word in ["approval", "approve"]):
        flows.append("Approval Process Flow")
    if any(word in combined_text for word in ["notification", "notify", "alert"]):
        flows.append("Notification Flow")
    if any(word in combined_text for word in ["lead", "convert"]):
        flows.append("Lead Conversion Flow")
    if any(word in combined_text for word in ["opportunity", "stage"]):
        flows.append("Opportunity Management Flow")

    # Remove duplicates
    objects = list(set(objects))
    flows = list(set(flows))

    return {
        "objects": objects,
        "fields": fields,
        "flows": flows
    }


def get_mapping_rules() -> Dict[str, Any]:
    """Get the current Salesforce mapping rules configuration."""
    return SALESFORCE_MAPPING_RULES.copy()


def update_mapping_rules(new_rules: Dict[str, Any]) -> None:
    """Update the Salesforce mapping rules (for customization)."""
    global SALESFORCE_MAPPING_RULES
    if isinstance(new_rules, dict):
        SALESFORCE_MAPPING_RULES.update(new_rules)


# Legacy function for backward compatibility
def map_to_salesforce(artifact: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function - convert artifact to Salesforce mapping."""
    requirements = artifact.get("requirements", [])
    pain_points = artifact.get("pain_points", [])

    return map_requirements_to_salesforce(requirements, pain_points)
