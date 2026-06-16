from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TargetCreate(BaseModel):
    data_type: str
    value: str
    file_path: str | None = None


class AnalysisCreate(BaseModel):
    target_name: str | None = None
    notes: str | None = None
    username: str | None = None
    ip_address: str | None = None
    email: str | None = None
    url: str | None = None


class FindingResponse(BaseModel):
    id: UUID
    module: str
    category: str
    key: str
    value: str
    confidence: float | None
    source: str | None
    raw_data: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LocationResponse(BaseModel):
    id: UUID
    latitude: float
    longitude: float
    accuracy_meters: int | None
    source: str
    timestamp: datetime | None
    address: str | None
    confidence: float | None

    model_config = {"from_attributes": True}


class TargetResponse(BaseModel):
    id: UUID
    data_type: str
    value: str
    file_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisResponse(BaseModel):
    id: UUID
    created_at: datetime
    status: str
    target_name: str | None
    notes: str | None
    confidence_score: float
    targets: list[TargetResponse] = []
    findings: list[FindingResponse] = []
    locations: list[LocationResponse] = []

    model_config = {"from_attributes": True}


class AnalysisStartResponse(BaseModel):
    analysis_id: str
    status: str


class AnalysisListItem(BaseModel):
    id: UUID
    created_at: datetime
    status: str
    target_name: str | None
    confidence_score: float

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_analyses: int
    this_month: int
    avg_confidence: float


class ModuleStatusUpdate(BaseModel):
    event: str = "module_complete"
    module: str
    status: str = "completed"
    findings_count: int = 0
    findings: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None
    timestamp: str
