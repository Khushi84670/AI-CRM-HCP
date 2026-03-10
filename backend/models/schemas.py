from datetime import date, time
from typing import Optional, List

from pydantic import BaseModel, Field


class HCPBase(BaseModel):
    name: str = Field(..., example="Dr. John Smith")
    specialization: Optional[str] = Field(None, example="Cardiologist")
    hospital: Optional[str] = Field(None, example="City Hospital")


class HCPCreate(HCPBase):
    pass


class HCPRead(HCPBase):
    id: int

    class Config:
        from_attributes = True


class InteractionBase(BaseModel):
    hcp_name: str = Field(..., example="Dr. John Smith")
    interaction_type: str = Field(..., example="Meeting")
    date: date
    time: time
    attendees: Optional[str] = None
    topics: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = Field(None, example="Positive")
    outcomes: Optional[str] = None
    followup_actions: Optional[str] = None
    summary: Optional[str] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionRead(InteractionBase):
    id: int
    hcp_id: int

    class Config:
        from_attributes = True


class InteractionUpdate(BaseModel):
    interaction_type: Optional[str] = None
    date: Optional[date] = None
    time: Optional[time] = None
    attendees: Optional[str] = None
    topics: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    followup_actions: Optional[str] = None
    summary: Optional[str] = None


class AIInteractionRequest(BaseModel):
    input_text: str
    existing_interaction_id: Optional[int] = None


class AIToolResult(BaseModel):
    message: str
    interaction: Optional[InteractionRead] = None
    followup_suggestions: Optional[List[str]] = None

