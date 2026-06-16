from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: UUID
    analysis_id: UUID
    format: str
    file_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
