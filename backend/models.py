# models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ContentRequest(BaseModel):
    text: str
    metadata: Optional[Dict] = Field(default_factory=dict)
    tenant_id: str

class ContentResponse(BaseModel):
    id: str
    text: str
    metadata: Dict
    analysis: Dict
    created_at: str
    updated_at: str
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
class Contentanalysis(BaseModel):
    id: str
    text: str
    analysis: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
class SearchRequest(BaseModel):
    query: str
    tenant_id: str
    filters: Optional[Dict] = Field(default_factory=dict)
