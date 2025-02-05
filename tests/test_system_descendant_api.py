import pytest

from fastapi.testclient import TestClient
from ad_context_svc.app import app
from ad_context_svc.models.system import System, SystemRelation


# Helper function to create a system
def create_system(db, system_id, name):
    system = System(id=system_id, name=name, description="test system")
    db.add(system)
    db.commit()
    return system


@pytest.fixture
def setup_systems(db_session):
    # Create systems
    system1 = create_system(db_session, 1, "System 1")
    system2 = create_system(db_session, 2, "System 2")
    system3 = create_system(db_session, 3, "System 3")
    # Create relations: 1 -> 2, 2 -> 3
    relation1 = SystemRelation(parent_id=system1.id, child_id=system2.id)
    relation2 = SystemRelation(parent_id=system2.id, child_id=system3.id)
    db_session.add_all([relation1, relation2])
    db_session.commit()
    return system1, system2, system3


@pytest.fixture
def client_fixture(client):
    return client


def test_get_descendant_not_found(client_fixture):
    # When system does not exist
    response = client_fixture.get("/system/descendant?system_id=999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_descendant_empty(client_fixture, db_session):
    # Create a system without descendants
    system = create_system(db_session, 10, "System 10")
    response = client_fixture.get(f"/system/descendant?system_id={system.id}")
    assert response.status_code == 404
    assert "no descendant" in response.json()["detail"].lower()


def test_get_descendant_success(client_fixture, db_session, setup_systems):
    system1, system2, system3 = setup_systems
    response = client_fixture.get(f"/system/descendant?system_id={system1.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["system_id"] == system1.id
    # Expect descendants to include system2 and system3 ids
    assert set(data["descendants"]) == {system2.id, system3.id}
