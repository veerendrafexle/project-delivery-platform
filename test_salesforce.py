"""Test script for Salesforce mapping without network calls."""
import json
from pathlib import Path
from unittest.mock import patch

from app.salesforce_mapper import map_requirements_to_salesforce


def mock_call_llm(prompt: str, **kwargs) -> dict:
    """Mock LLM response for testing."""
    if "Salesforce" in prompt or "salesforce" in prompt:
        return {
            "objects": ["Lead", "Opportunity", "Account"],
            "fields": {
                "customer_name": "Name",
                "email": "Email",
                "deal_amount": "Amount",
                "close_date": "CloseDate",
                "lead_status": "Status"
            },
            "flows": ["Lead Conversion Flow", "Opportunity Management Flow"]
        }
    else:
        return {"error": "Mock response"}


def test_salesforce_mapping():
    """Test the Salesforce mapping module."""
    print("Testing Salesforce Mapping...")

    # Test requirements and pain points
    requirements = [
        "Track customer leads and convert them to opportunities",
        "Manage sales pipeline with deal amounts and close dates",
        "Send email notifications for lead status changes",
        "Automate lead assignment based on criteria"
    ]

    pain_points = [
        "Manual lead tracking is time-consuming",
        "No visibility into sales pipeline",
        "Lead follow-up is inconsistent"
    ]

    context_chunks = [
        "Sales team needs better lead management",
        "Current CRM system lacks automation"
    ]

    # Mock the AI call
    with patch('app.salesforce_mapper.call_llm', side_effect=mock_call_llm):
        mapping = map_requirements_to_salesforce(
            requirements=requirements,
            pain_points=pain_points,
            context_chunks=context_chunks
        )

    print(f"Generated mapping with {len(mapping['objects'])} objects, {len(mapping['fields'])} fields, {len(mapping['flows'])} flows")

    # Verify structure
    expected_keys = {"objects", "fields", "flows"}
    if expected_keys.issubset(mapping.keys()):
        print("✅ Mapping structure is correct")
    else:
        print("❌ Mapping structure is missing keys")
        return False

    # Verify objects are strings
    if all(isinstance(obj, str) for obj in mapping["objects"]):
        print("✅ Objects are properly formatted")
    else:
        print("❌ Objects are not strings")
        return False

    # Verify fields are dict with string values
    if isinstance(mapping["fields"], dict):
        if all(isinstance(k, str) and isinstance(v, str) for k, v in mapping["fields"].items()):
            print("✅ Fields are properly formatted")
        else:
            print("❌ Fields are not string key-value pairs")
            return False
    else:
        print("❌ Fields is not a dictionary")
        return False

    # Verify flows are strings
    if all(isinstance(flow, str) for flow in mapping["flows"]):
        print("✅ Flows are properly formatted")
    else:
        print("❌ Flows are not strings")
        return False

    # Save test result
    output_path = Path("test_salesforce_mapping.json")
    with open(output_path, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"✅ Salesforce mapping saved to {output_path}")
    print(f"Sample output: {json.dumps(mapping, indent=2)}")

    return True


def test_fallback_mapping():
    """Test the fallback mapping when AI fails."""
    print("\nTesting Fallback Mapping...")

    requirements = [
        "Track customer leads",
        "Manage opportunities with amounts",
        "Send notifications"
    ]

    pain_points = ["Manual processes are slow"]

    # Mock AI failure
    with patch('app.salesforce_mapper.call_llm', return_value=None):
        mapping = map_requirements_to_salesforce(requirements, pain_points)

    if mapping["objects"] and mapping["fields"] and mapping["flows"]:
        print("✅ Fallback mapping generated valid output")
        return True
    else:
        print("❌ Fallback mapping failed")
        return False


if __name__ == "__main__":
    success1 = test_salesforce_mapping()
    success2 = test_fallback_mapping()

    if success1 and success2:
        print("\n🎉 All Salesforce mapping tests PASSED")
    else:
        print("\n❌ Some tests FAILED")