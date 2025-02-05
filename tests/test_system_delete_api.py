import pytest
from sqlalchemy import text

from ad_context_svc.models.system import System, SystemRelation


def test_delete_system_valid(client, db_session):
    # Setup: Create a test system record
    system = System(name="Test System", description="Test Description")
    db_session.add(system)
    db_session.commit()
    system_id = system.id

    # Add a system relation record linked to this system (self-relation for testing)
    relation = SystemRelation(parent_id=system_id, child_id=system_id)
    db_session.add(relation)
    db_session.commit()

    # Delete the system record using the DELETE endpoint
    response = client.delete("/system/delete", params={"system_id": system_id})
    assert response.status_code == 200
    data = response.json()
    assert "detail" in data

    # Verify that the system is deleted
    stmt = text("SELECT * FROM systems WHERE id = :id")
    result = db_session.execute(stmt, {'id': system_id}).fetchone()
    assert result is None


def test_delete_system_invalid(client):
    # Attempt to delete a non-existent system record
    response = client.delete("/system/delete", params={"system_id": 9999})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
