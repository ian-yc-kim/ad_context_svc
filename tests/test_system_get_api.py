import pytest

from ad_context_svc.models.system import System


def test_get_system_valid(client, db_session):
    # Insert a test system record into the in-memory database
    test_system = System(
        name="Test System",
        description="A test system",
        codebase_id=1,
        database_id=1,
        service_url="http://example.com",
        config={"key": "value"},
        system_summary="A summary",
        is_deleted=False
    )
    session = db_session  # Use the fixture instance directly without calling it
    session.add(test_system)
    session.commit()
    session.refresh(test_system)

    response = client.get(f"/system/get?system_id={test_system.id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == test_system.id
    assert data["name"] == "Test System"
    assert data["description"] == "A test system"


def test_get_system_invalid_parameter(client):
    # Non-integer system_id should result in a 422 Unprocessable Entity error
    response = client.get("/system/get?system_id=abc")
    assert response.status_code == 422


def test_get_system_not_found(client):
    # Request a system_id that does not exist; expecting a 404 Not Found
    response = client.get("/system/get?system_id=9999")
    assert response.status_code == 404
