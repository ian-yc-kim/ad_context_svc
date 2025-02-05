import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from ad_context_svc.models.system import System
from ad_context_svc.models.base import get_db

router = APIRouter()

def _system_to_dict(system: System) -> dict:
    return {
        "id": system.id,
        "name": system.name,
        "description": system.description,
        "codebase_id": system.codebase_id,
        "database_id": system.database_id,
        "service_url": system.service_url,
        "config": system.config,
        "system_summary": system.system_summary,
        "is_deleted": system.is_deleted,
    }

@router.get("/get")
async def get_system(system_id: int, db: Session = Depends(get_db)):
    try:
        result = db.execute(select(System).where(System.id == system_id)).scalar_one_or_none()
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    if result is None:
        raise HTTPException(status_code=404, detail="System not found")

    return _system_to_dict(result)
