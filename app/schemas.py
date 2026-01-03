"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from uuid import UUID


class MemoryItemBase(BaseModel):
    """Base schema for memory items."""
    content: str = Field(..., description="The content of the memory item")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional metadata")
    entity_type: Optional[str] = Field(None, description="Type of entity for knowledge graph")
    created_by: Optional[str] = Field(None, description="Agent or user who created this memory")


class MemoryItemCreate(MemoryItemBase):
    """Schema for creating a new memory item."""
    pass


class MemoryItemUpdate(BaseModel):
    """Schema for updating a memory item."""
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    entity_type: Optional[str] = None
    updated_by: Optional[str] = None
    version: Optional[int] = Field(None, description="Expected version for optimistic locking")


class MemoryItemResponse(MemoryItemBase):
    """Schema for memory item response."""
    id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class MemoryItemSearch(BaseModel):
    """Schema for semantic search request."""
    query: str = Field(..., description="Text query for semantic search")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class MemoryItemSearchResponse(BaseModel):
    """Schema for search response."""
    results: List[MemoryItemResponse]
    count: int
    query: str


class KnowledgeLinkCreate(BaseModel):
    """Schema for creating a knowledge link."""
    source_id: UUID = Field(..., description="Source memory item ID")
    target_id: UUID = Field(..., description="Target memory item ID")
    relationship_type: str = Field(..., description="Type of relationship")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_by: Optional[str] = None


class KnowledgeLinkResponse(BaseModel):
    """Schema for knowledge link response."""
    id: UUID
    source_id: UUID
    target_id: UUID
    relationship_type: str
    metadata: Dict[str, Any]
    valid_from: datetime
    valid_to: Optional[datetime]
    created_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    database: str
    version: str = "1.0.0"

