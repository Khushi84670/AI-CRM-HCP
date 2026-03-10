from typing import List, Optional

from sqlalchemy.orm import Session

from models import entities
from models.schemas import (
    HCPCreate,
    HCPRead,
    InteractionCreate,
    InteractionRead,
    InteractionUpdate,
)


def get_or_create_hcp(db: Session, hcp_in: HCPCreate) -> entities.HCP:
    hcp = (
        db.query(entities.HCP)
        .filter(entities.HCP.name == hcp_in.name)
        .first()
    )
    if hcp:
        return hcp
    hcp = entities.HCP(
        name=hcp_in.name,
        specialization=hcp_in.specialization,
        hospital=hcp_in.hospital,
    )
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


def create_interaction(db: Session, interaction_in: InteractionCreate) -> entities.Interaction:
    hcp = get_or_create_hcp(
        db,
        HCPCreate(
            name=interaction_in.hcp_name,
            specialization=None,
            hospital=None,
        ),
    )

    interaction = entities.Interaction(
        hcp_id=hcp.id,
        interaction_type=interaction_in.interaction_type,
        date=interaction_in.date,
        time=interaction_in.time,
        attendees=interaction_in.attendees,
        topics=interaction_in.topics,
        materials_shared=interaction_in.materials_shared,
        samples_distributed=interaction_in.samples_distributed,
        sentiment=interaction_in.sentiment,
        outcomes=interaction_in.outcomes,
        followup_actions=interaction_in.followup_actions,
        summary=interaction_in.summary,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def list_interactions(db: Session) -> List[entities.Interaction]:
    return db.query(entities.Interaction).order_by(
        entities.Interaction.date.desc(), entities.Interaction.time.desc()
    ).all()


def get_interaction(db: Session, interaction_id: int) -> Optional[entities.Interaction]:
    return (
        db.query(entities.Interaction)
        .filter(entities.Interaction.id == interaction_id)
        .first()
    )


def update_interaction(
    db: Session, interaction_id: int, interaction_in: InteractionUpdate
) -> Optional[entities.Interaction]:
    interaction = get_interaction(db, interaction_id)
    if not interaction:
        return None

    data = interaction_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return interaction


def get_hcp_history(db: Session, hcp_name: str) -> List[entities.Interaction]:
    hcp = (
        db.query(entities.HCP)
        .filter(entities.HCP.name.ilike(hcp_name))
        .first()
    )
    if not hcp:
        return []

    return (
        db.query(entities.Interaction)
        .filter(entities.Interaction.hcp_id == hcp.id)
        .order_by(
            entities.Interaction.date.desc(),
            entities.Interaction.time.desc(),
        )
        .all()
    )

