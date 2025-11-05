from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .log_db import Base

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    author = Column(String(128))
    body = Column(Text, nullable=False)

    # Structured tags
    node_code = Column(Integer, nullable=True)
    input_code = Column(Integer, nullable=True)
    tags = Column(JSONB, nullable=False, server_default="{}")

    # Tamper-evident chain of custody
    prev_hash = Column(String(64))
    curr_hash = Column(String(64))

    supersedes_id = Column(Integer, ForeignKey("log_entries.id"), nullable=True)
    superseded_by = relationship("LogEntry", remote_side=[id], uselist=False)

    Index("idx_log_created", LogEntry.created_utc.desc())
    Index("idx_log_node_input", LogEntry.node_code, LogEntry.input_code)
