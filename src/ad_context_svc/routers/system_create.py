import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ad_context_svc.models.base import get_db
from ad_context_svc.models.system import System, SystemRelation

logger = logging.getLogger(__name__)

router = APIRouter()


class SystemCreateRequest(BaseModel):
    name: str
    description: str
    parent_id: Optional[int] = None


@router.post("/create")
def create_system(request: SystemCreateRequest, db: Session = Depends(get_db)):
    try:
        if request.parent_id:
            parent = db.query(System).filter(System.id == request.parent_id).first()
            if not parent:
                logger.error(f"Parent system with id {request.parent_id} not found.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent system not found")
        new_system = System(name=request.name, description=request.description)
        db.add(new_system)
        db.flush()  # Flush to obtain new system id
        if request.parent_id:
            relation = SystemRelation(parent_id=request.parent_id, child_id=new_system.id)
            db.add(relation)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating system")

    return {"message": "System created successfully", "system_id": new_system.id}
