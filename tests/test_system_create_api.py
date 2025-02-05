import pytest
from fastapi.testclient import TestClient

from ad_context_svc.models.system import System, SystemRelation


# Test successful creation of a system without a parent
def test_create_system_without_parent(client, db_session):
    payload = {
        "name": "System A",
        "description": "Description for System A"
    }
    response = client.post("/system/create", json=payload)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, response: {response.text}"
    data = response.json()
    assert data.get("message") == "System created successfully"
    system_id = data.get("system_id")
    assert system_id is not None

    # Verify that the system exists in the database
    system = db_session.query(System).filter(System.id == system_id).first()
    assert system is not None
    assert system.name == "System A"
    assert system.description == "Description for System A"


# Test successful creation of a system with a valid parent
def test_create_system_with_parent(client, db_session):
    # First, create a parent system
    parent_payload = {
        "name": "Parent System",
        "description": "Parent system description"
    }
    parent_response = client.post("/system/create", json=parent_payload)
    assert parent_response.status_code == 200, f"Parent creation failed: {parent_response.text}"
    parent_data = parent_response.json()
    parent_id = parent_data.get("system_id")
    assert parent_id is not None

    # Now create a child system with the valid parent_id
    child_payload = {
        "name": "Child System",
        "description": "Child system description",
        "parent_id": parent_id
    }
    child_response = client.post("/system/create", json=child_payload)
    assert child_response.status_code == 200, f"Child creation failed: {child_response.text}"
    child_data = child_response.json()
    child_system_id = child_data.get("system_id")
    assert child_system_id is not None

    # Verify that the child system exists
    child_system = db_session.query(System).filter(System.id == child_system_id).first()
    assert child_system is not None
    assert child_system.name == "Child System"

    # Verify the system relation between parent and child
    relation = db_session.query(SystemRelation).filter(
        SystemRelation.parent_id == parent_id,
        SystemRelation.child_id == child_system_id
    ).first()
    assert relation is not None


# Test error response when required fields are missing
def test_create_system_missing_required_fields(client):
    # Missing both name and description
    payload = {}
    response = client.post("/system/create", json=payload)
    # FastAPI validation error returns 422
    assert response.status_code == 422, f"Expected 422 due to missing fields but got {response.status_code}"

    # Test missing only description
    payload_missing_description = {"name": "System B"}
    response = client.post("/system/create", json=payload_missing_description)
    assert response.status_code == 422, f"Expected 422 due to missing description but got {response.status_code}"

    # Test missing only name
    payload_missing_name = {"description": "Description for System B"}
    response = client.post("/system/create", json=payload_missing_name)
    assert response.status_code == 422, f"Expected 422 due to missing name but got {response.status_code}"


# Test error response when an invalid/non-existent parent_id is provided
def test_create_system_invalid_parent(client):
    payload = {
        "name": "System C",
        "description": "Description for System C",
        "parent_id": 9999  # Assumed to be non-existent
    }
    response = client.post("/system/create", json=payload)
    assert response.status_code == 404, f"Expected 404 for non-existent parent, got {response.status_code}"
    data = response.json()
    assert data.get("detail") == "Parent system not found"
