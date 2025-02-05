import logging

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import Session

from ad_context_svc.models import System, SystemRelation, get_db

router = APIRouter()

@router.delete("/delete")
async def delete_system(
    system_id: int = Query(..., description="ID of the system to delete"),
    db: Session = Depends(get_db)
):
    try:
        # Verify the existence of the system
        stmt = select(System).filter(System.id == system_id)
        result = db.execute(stmt)
        system = result.scalars().first()
        if not system:
            raise HTTPException(status_code=404, detail=f"System with id {system_id} not found.")

        # Delete associated system relations where the system is referenced as parent or child
        del_stmt = delete(SystemRelation).where(
            or_(
                SystemRelation.parent_id == system_id,
                SystemRelation.child_id == system_id
            )
        )
        db.execute(del_stmt)

        # Delete the system record
        db.delete(system)
        db.commit()
        return {"detail": f"System with id {system_id} deleted successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during deletion.")
