from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from .base import Base


class System(Base):
    __tablename__ = 'systems'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(String(1024), nullable=False)
    codebase_id = Column(Integer, nullable=True)
    database_id = Column(Integer, nullable=True)
    service_url = Column(String(256), nullable=True, comment='URL with validation should be applied at application level')
    config = Column(JSON, nullable=True)
    system_summary = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<System(id={self.id}, name='{self.name}')>"


class SystemRelation(Base):
    __tablename__ = 'system_relations'

    parent_id = Column(Integer, ForeignKey('systems.id'), primary_key=True, nullable=False)
    child_id = Column(Integer, ForeignKey('systems.id'), primary_key=True, nullable=False)

    parent = relationship('System', foreign_keys=[parent_id], backref='child_relations')
    child = relationship('System', foreign_keys=[child_id], backref='parent_relations')

    def __repr__(self) -> str:
        return f"<SystemRelation(parent_id={self.parent_id}, child_id={self.child_id})>"
