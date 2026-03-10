from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text
from sqlalchemy.orm import relationship

from .database import Base


class HCP(Base):
    __tablename__ = "hcp"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    specialization = Column(String(255), nullable=True)
    hospital = Column(String(255), nullable=True)

    interactions = relationship("Interaction", back_populates="hcp")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcp.id"), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    attendees = Column(Text, nullable=True)
    topics = Column(Text, nullable=True)
    materials_shared = Column(Text, nullable=True)
    samples_distributed = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)
    outcomes = Column(Text, nullable=True)
    followup_actions = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    hcp = relationship("HCP", back_populates="interactions")

