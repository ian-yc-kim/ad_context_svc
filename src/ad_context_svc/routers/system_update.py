from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
import logging

from pydantic import BaseModel

from ad_context_svc.models import System, SystemRelation
from ad_context_svc.models.base import get_db


router = APIRouter()


class SystemUpdateRequest(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


@router.put("/system/update")
def update_system(request: SystemUpdateRequest, db: Session = Depends(get_db)):
    try:
        # Retrieve the existing system record
        system = db.query(System).filter(System.id == request.id, System.is_deleted == False).first()
        if not system:
            raise HTTPException(status_code=404, detail="System not found")

        # Check for existing parent-child relation
        current_relation = db.query(SystemRelation).filter(SystemRelation.child_id == request.id).first()
        current_parent_id = current_relation.parent_id if current_relation else None

        # If parent_id is provided and changed
        if request.parent_id is not None and request.parent_id != current_parent_id:
            if request.parent_id == request.id:
                raise HTTPException(status_code=400, detail="System cannot be its own parent")
            new_parent = db.query(System).filter(System.id == request.parent_id, System.is_deleted == False).first()
            if not new_parent:
                raise HTTPException(status_code=404, detail="Parent system not found")
            if current_relation:
                current_relation.parent_id = request.parent_id
            else:
                new_relation = SystemRelation(parent_id=request.parent_id, child_id=request.id)
                db.add(new_relation)
        
        # Update system fields
        if request.name is not None:
            system.name = request.name
        if request.description is not None:
            system.description = request.description

        db.commit()
        db.refresh(system)

        return {"detail": "System updated successfully", "system": {"id": system.id, "name": system.name, "description": system.description}}
    except HTTPException as http_e:
        db.rollback()
        logging.error(http_e, exc_info=True)
        raise http_e
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        db.rollback()
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
