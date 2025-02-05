import pytest
from fastapi import status

from ad_context_svc.models.system import System, SystemRelation


def test_create_system_without_parent(client, db_session):
    payload = {
        "name": "New System",
        "description": "A new system"
    }
    # Updated endpoint to include '/system' prefix
    response = client.post("/system/create", json=payload)
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert "system_id" in json_data

    # Verify the system is created in the database
    created_system = db_session.query(System).filter_by(id=json_data["system_id"]).first()
    assert created_system is not None
    assert created_system.name == "New System"


def test_create_system_missing_fields(client):
    # Missing required field 'name'
    payload = {
        "description": "Desc without name"
    }
    response = client.post("/system/create", json=payload)
    # FastAPI/Pydantic returns 422 Unprocessable Entity for validation errors
    assert response.status_code == 422


def test_create_system_with_parent(client, db_session):
    # Create a parent system first
    parent = System(name="Parent System", description="Parent description")
    db_session.add(parent)
    db_session.commit()

    payload = {
        "name": "Child System",
        "description": "Child system description",
        "parent_id": parent.id
    }
    response = client.post("/system/create", json=payload)
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    child_id = json_data["system_id"]

    # Verify the child system and its relation in the database
    child = db_session.query(System).filter_by(id=child_id).first()
    assert child is not None
    relation = db_session.query(SystemRelation).filter_by(parent_id=parent.id, child_id=child_id).first()
    assert relation is not None
