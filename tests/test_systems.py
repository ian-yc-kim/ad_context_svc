from sqlalchemy.exc import IntegrityError
import pytest

from ad_context_svc.models.system import System, SystemRelation

def test_create_system(db_session):
    # create a system
    system = System(
        name="Test System",
        description="A test system",
        codebase_id=1,
        database_id=1,
        service_url="http://example.com",
        config={"key": "value"},
        system_summary="Summary",
        is_deleted=False
    )
    db_session.add(system)
    db_session.commit()

    result = db_session.query(System).filter_by(name="Test System").first()
    assert result is not None
    assert result.description == "A test system"


def test_unique_system_name(db_session):
    # create a system with unique name constraint, then try to insert duplicate name
    system1 = System(name="Unique System", description="desc1")
    db_session.add(system1)
    db_session.commit()

    system2 = System(name="Unique System", description="desc2")
    db_session.add(system2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_system_relation(db_session):
    # Test creating system relation
    parent = System(name="Parent System", description="Parent")
    child = System(name="Child System", description="Child")
    db_session.add_all([parent, child])
    db_session.commit()

    relation = SystemRelation(parent_id=parent.id, child_id=child.id)
    db_session.add(relation)
    db_session.commit()

    result = db_session.query(SystemRelation).filter_by(parent_id=parent.id, child_id=child.id).first()
    assert result is not None
