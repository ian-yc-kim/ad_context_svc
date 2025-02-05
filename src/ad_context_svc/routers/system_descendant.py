from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

from ad_context_svc.models.base import get_db
from ad_context_svc.models.system import System, SystemRelation

router = APIRouter()

@router.get("/descendant", summary="Retrieve descendant systems")
def get_descendants(system_id: int = Query(..., description="ID of the system to fetch descendants for"), db: Session = Depends(get_db)):
    """
    Endpoint to retrieve all descendant systems for a given system ID using a recursive CTE.
    """
    try:
        # Validate that the system exists
        system = db.query(System).filter(System.id == system_id).first()
        if not system:
            raise HTTPException(status_code=404, detail=f"System with id {system_id} not found")
        
        # Create a recursive CTE to fetch descendant system IDs
        descendant_cte = (
            select(SystemRelation.child_id)
            .where(SystemRelation.parent_id == system_id)
            .cte(name="descendant_cte", recursive=True)
        )
        descendant_alias = descendant_cte.alias()
        descendant_cte = descendant_cte.union_all(
            select(SystemRelation.child_id)
            .where(SystemRelation.parent_id == descendant_alias.c.child_id)
        )

        # Execute the query to get descendant system IDs
        result = db.execute(select(descendant_cte.c.child_id)).fetchall()
        descendant_ids = [row[0] for row in result]

        if not descendant_ids:
            raise HTTPException(status_code=404, detail="No descendant systems found")
        
        return {"system_id": system_id, "descendants": descendant_ids}
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
