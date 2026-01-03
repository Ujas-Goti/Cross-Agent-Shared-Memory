"""SQLAlchemy models for CASM database."""
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
from app.database import Base


class MemoryItem(Base):
    """Model for storing memory items."""
    __tablename__ = "memory_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)
    embedding = Column(Vector(384))  # Dimension for all-MiniLM-L6-v2
    
    # Versioning and tracking
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255))
    updated_by = Column(String(255))
    
    # Optional fields for knowledge graph
    entity_type = Column(String(100))
    relationships = Column(JSON, default=list)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_memory_created_at', 'created_at'),
        Index('idx_memory_entity_type', 'entity_type'),
        Index('idx_memory_embedding', 'embedding', postgresql_using='ivfflat'),
    )
    
    def __repr__(self):
        return f"<MemoryItem(id={self.id}, content={self.content[:50]}...)>"


class KnowledgeLink(Base):
    """Model for knowledge graph relationships."""
    __tablename__ = "knowledge_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)
    relationship_type = Column(String(100), nullable=False)
    metadata = Column(JSON, default=dict)
    
    # Temporal information
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_to = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))
    
    __table_args__ = (
        Index('idx_knowledge_source', 'source_id'),
        Index('idx_knowledge_target', 'target_id'),
        Index('idx_knowledge_relationship', 'relationship_type'),
    )
    
    def __repr__(self):
        return f"<KnowledgeLink(source={self.source_id}, target={self.target_id}, type={self.relationship_type})>"

