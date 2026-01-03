"""Memory API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from uuid import UUID

from app.database import get_db
from app.schemas import (
    MemoryItemCreate,
    MemoryItemUpdate,
    MemoryItemResponse,
    MemoryItemSearch,
    MemoryItemSearchResponse
)
from app.services.memory import MemoryService
from app.services.auth import verify_api_key

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("", response_model=MemoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    memory_data: MemoryItemCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new memory item."""
    service = MemoryService(db)
    try:
        memory_item = service.create_memory(memory_data)
        return memory_item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating memory: {str(e)}"
        )


@router.get("/{memory_id}", response_model=MemoryItemResponse)
def get_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get a memory item by ID."""
    service = MemoryService(db)
    memory_item = service.get_memory(memory_id)
    
    if not memory_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory item {memory_id} not found"
        )
    
    return memory_item


@router.get("", response_model=list[MemoryItemResponse])
def list_memories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[str] = None,
    created_by: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List memory items with optional filters."""
    service = MemoryService(db)
    
    filters = {}
    if entity_type:
        filters["entity_type"] = entity_type
    if created_by:
        filters["created_by"] = created_by
    
    memories = service.list_memories(skip=skip, limit=limit, filters=filters if filters else None)
    return memories


@router.put("/{memory_id}", response_model=MemoryItemResponse)
def update_memory(
    memory_id: UUID,
    memory_data: MemoryItemUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update a memory item."""
    service = MemoryService(db)
    
    try:
        memory_item = service.update_memory(memory_id, memory_data)
        
        if not memory_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory item {memory_id} not found"
            )
        
        return memory_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating memory: {str(e)}"
        )


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a memory item."""
    service = MemoryService(db)
    
    success = service.delete_memory(memory_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory item {memory_id} not found"
        )


@router.post("/search", response_model=MemoryItemSearchResponse)
def search_memories(
    search_data: MemoryItemSearch,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Semantic search for memories."""
    service = MemoryService(db)
    
    try:
        results = service.search_memories(
            query_text=search_data.query,
            limit=search_data.limit,
            threshold=search_data.threshold,
            filters=search_data.filters
        )
        
        # Convert to response format
        memory_items = [item for item, score in results]
        
        return MemoryItemSearchResponse(
            results=memory_items,
            count=len(memory_items),
            query=search_data.query
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching memories: {str(e)}"
        )


@router.get("/{memory_id}/related", response_model=list[MemoryItemResponse])
def get_related_memories(
    memory_id: UUID,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get memories related to a given memory through knowledge links."""
    service = MemoryService(db)
    
    # Verify memory exists
    memory = service.get_memory(memory_id)
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory item {memory_id} not found"
        )
    
    related = service.get_related_memories(memory_id)
    return related

