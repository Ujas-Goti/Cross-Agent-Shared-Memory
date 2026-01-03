"""Service for memory operations."""
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.models import MemoryItem, KnowledgeLink
from app.schemas import MemoryItemCreate, MemoryItemUpdate
from app.services.embedding import embedding_service
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing memory items."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_memory(self, memory_data: MemoryItemCreate) -> MemoryItem:
        """Create a new memory item with embedding."""
        try:
            # Generate embedding
            embedding = embedding_service.generate_embedding(memory_data.content)
            
            # Create memory item
            memory_item = MemoryItem(
                content=memory_data.content,
                metadata=memory_data.metadata or {},
                entity_type=memory_data.entity_type,
                created_by=memory_data.created_by,
                embedding=embedding
            )
            
            self.db.add(memory_item)
            self.db.commit()
            self.db.refresh(memory_item)
            
            logger.info(f"Created memory item {memory_item.id}")
            return memory_item
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating memory: {str(e)}")
            raise
    
    def get_memory(self, memory_id: UUID) -> Optional[MemoryItem]:
        """Get a memory item by ID."""
        return self.db.query(MemoryItem).filter(MemoryItem.id == memory_id).first()
    
    def list_memories(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemoryItem]:
        """List memory items with optional filters."""
        query = self.db.query(MemoryItem)
        
        if filters:
            if "entity_type" in filters:
                query = query.filter(MemoryItem.entity_type == filters["entity_type"])
            if "created_by" in filters:
                query = query.filter(MemoryItem.created_by == filters["created_by"])
        
        return query.order_by(MemoryItem.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_memory(
        self,
        memory_id: UUID,
        memory_data: MemoryItemUpdate,
        updated_by: Optional[str] = None
    ) -> Optional[MemoryItem]:
        """Update a memory item with conflict detection."""
        memory_item = self.get_memory(memory_id)
        
        if not memory_item:
            return None
        
        # Optimistic locking: check version if provided
        if memory_data.version is not None and memory_item.version != memory_data.version:
            raise ValueError(
                f"Version conflict: expected version {memory_data.version}, "
                f"but current version is {memory_item.version}"
            )
        
        # Update fields
        if memory_data.content is not None:
            memory_item.content = memory_data.content
            # Regenerate embedding if content changed
            memory_item.embedding = embedding_service.generate_embedding(memory_data.content)
        
        if memory_data.metadata is not None:
            memory_item.metadata = memory_data.metadata
        
        if memory_data.entity_type is not None:
            memory_item.entity_type = memory_data.entity_type
        
        memory_item.version += 1
        memory_item.updated_by = updated_by or memory_data.updated_by
        
        try:
            self.db.commit()
            self.db.refresh(memory_item)
            logger.info(f"Updated memory item {memory_id}")
            return memory_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating memory: {str(e)}")
            raise
    
    def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory item."""
        memory_item = self.get_memory(memory_id)
        
        if not memory_item:
            return False
        
        try:
            self.db.delete(memory_item)
            self.db.commit()
            logger.info(f"Deleted memory item {memory_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting memory: {str(e)}")
            raise
    
    def search_memories(
        self,
        query_text: str,
        limit: int = 10,
        threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """Semantic search for memories using vector similarity."""
        # Generate embedding for query
        query_embedding = embedding_service.generate_embedding(query_text)
        
        # Build query
        query = self.db.query(
            MemoryItem,
            func.cosine_distance(MemoryItem.embedding, query_embedding).label('distance')
        ).filter(
            func.cosine_distance(MemoryItem.embedding, query_embedding) <= (1 - threshold)
        )
        
        # Apply filters
        if filters:
            if "entity_type" in filters:
                query = query.filter(MemoryItem.entity_type == filters["entity_type"])
            if "created_by" in filters:
                query = query.filter(MemoryItem.created_by == filters["created_by"])
        
        # Order by similarity (lower distance = higher similarity)
        query = query.order_by('distance').limit(limit)
        
        # Execute and return results
        results = query.all()
        
        # Convert distance to similarity score (1 - distance)
        return [(item, 1 - distance) for item, distance in results]
    
    def create_knowledge_link(
        self,
        source_id: UUID,
        target_id: UUID,
        relationship_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> KnowledgeLink:
        """Create a knowledge graph link between two memory items."""
        # Verify both memory items exist
        source = self.get_memory(source_id)
        target = self.get_memory(target_id)
        
        if not source or not target:
            raise ValueError("Source or target memory item not found")
        
        link = KnowledgeLink(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            metadata=metadata or {},
            created_by=created_by
        )
        
        try:
            self.db.add(link)
            self.db.commit()
            self.db.refresh(link)
            logger.info(f"Created knowledge link {link.id}")
            return link
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating knowledge link: {str(e)}")
            raise
    
    def get_related_memories(self, memory_id: UUID) -> List[MemoryItem]:
        """Get memories related to a given memory through knowledge links."""
        # Find all links where this memory is source or target
        links = self.db.query(KnowledgeLink).filter(
            (KnowledgeLink.source_id == memory_id) | (KnowledgeLink.target_id == memory_id)
        ).all()
        
        # Collect related memory IDs
        related_ids = set()
        for link in links:
            if link.source_id == memory_id:
                related_ids.add(link.target_id)
            else:
                related_ids.add(link.source_id)
        
        # Fetch related memories
        if related_ids:
            return self.db.query(MemoryItem).filter(MemoryItem.id.in_(related_ids)).all()
        return []

