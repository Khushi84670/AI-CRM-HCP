from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import get_db
from models.schemas import (
    InteractionCreate,
    InteractionRead,
    InteractionUpdate,
)
from services import db_service


router = APIRouter()


@router.post("/interactions", response_model=InteractionRead)
def create_interaction(
    interaction_in: InteractionCreate,
    db: Session = Depends(get_db),
) -> InteractionRead:
    interaction = db_service.create_interaction(db, interaction_in)
    return InteractionRead.from_orm(interaction).model_copy()


@router.get("/interactions", response_model=List[InteractionRead])
def list_all_interactions(
    db: Session = Depends(get_db),
) -> List[InteractionRead]:
    interactions = db_service.list_interactions(db)
    return [InteractionRead.from_orm(i).model_copy() for i in interactions]


@router.put("/interactions/{interaction_id}", response_model=InteractionRead)
def update_interaction(
    interaction_id: int,
    interaction_in: InteractionUpdate,
    db: Session = Depends(get_db),
) -> InteractionRead:
    interaction = db_service.update_interaction(db, interaction_id, interaction_in)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return InteractionRead.from_orm(interaction).model_copy()


@router.get("/hcp-history/{hcp_name}", response_model=List[InteractionRead])
def get_hcp_history(
    hcp_name: str,
    db: Session = Depends(get_db),
) -> List[InteractionRead]:
    interactions = db_service.get_hcp_history(db, hcp_name)
    return [InteractionRead.from_orm(i).model_copy() for i in interactions]

