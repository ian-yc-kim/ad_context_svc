import pytest

from ad_context_svc.models import System, SystemRelation
from ad_context_svc.models.base import get_db


def create_system_from_client(client, name, description):
    # Retrieve the session from the same dependency override used by the client
    db_generator = client.app.dependency_overrides[get_db]()
    session = next(db_generator)
    try:
        system = System(name=name, description=description)
        session.add(system)
        session.commit()
        session.refresh(system)
        return system
    finally:
        session.close()


def test_update_system_no_parent_change(client):
    # Create a system record using the same session as the client
    system = create_system_from_client(client, "System_A", "Desc A")
    
    # Update the system's name and description without modifying parent relation
    response = client.put("/system/update", json={"id": system.id, "name": "System_A_Updated", "description": "New Desc"})
    assert response.status_code == 200
    data = response.json()
    assert data["system"]["name"] == "System_A_Updated"
    
    # Verify that there is no system relation
    db_generator = client.app.dependency_overrides[get_db]()
    session = next(db_generator)
    try:
        relation = session.query(SystemRelation).filter(SystemRelation.child_id == system.id).first()
        assert relation is None
    finally:
        session.close()


def test_update_system_with_parent_change(client):
    # Create parent and child systems using the same session as the client
    parent = create_system_from_client(client, "Parent_System", "Parent Desc")
    child = create_system_from_client(client, "Child_System", "Child Desc")
    
    # Update the child system to set a new parent
    response = client.put("/system/update", json={"id": child.id, "parent_id": parent.id})
    assert response.status_code == 200
    
    # Verify the system relation is updated
    db_generator = client.app.dependency_overrides[get_db]()
    session = next(db_generator)
    try:
        relation = session.query(SystemRelation).filter(SystemRelation.child_id == child.id).first()
        assert relation is not None
        assert relation.parent_id == parent.id
    finally:
        session.close()


def test_update_system_invalid_system_id(client):
    # Attempt to update a non-existent system
    response = client.put("/system/update", json={"id": 9999, "name": "Doesn't matter"})
    assert response.status_code == 404


def test_update_system_invalid_parent_id(client):
    # Create a system using the same session as the client
    system = create_system_from_client(client, "System_Invalid", "Desc")
    
    # Attempt to update with a non-existent parent id
    response = client.put("/system/update", json={"id": system.id, "parent_id": 8888})
    assert response.status_code == 404


def test_update_system_self_parent(client):
    # Create a system using the same session as the client
    system = create_system_from_client(client, "System_Self", "Desc")
    
    # Attempt to set the system as its own parent
    response = client.put("/system/update", json={"id": system.id, "parent_id": system.id})
    assert response.status_code == 400
