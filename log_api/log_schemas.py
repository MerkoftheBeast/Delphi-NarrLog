from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class LogCreate(BaseModel):
    body: str = Field(..., min_length=1)
    node_code: Optional[int] = None
    input_code: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None

    @validator("node_code")
    def _node_range(cls, v):
        if v is not None and (v < 0 or v > 99):
            raise ValueError("node_code must be 0..99 for Ndd")
        return v
    
    @validator("input_code")
    def _node_range(cls, v):
        if v is not None and (v < 0 or v > 999):
            raise ValueError("input_code must be 0..99 for Ndd")
        return v
    
class Logout(BaseModel):
    id: int
    created_utc: str
    author: str
    body: str
    node_code: Optional[int] = None
    input_code: Optional[int] = None
    tags: Dict[str, Any]
    prev_hash: Optional[str] = None
    curr_hash: str
    supersedes_id: Optional[int] = None

class IntegrityReport(BaseModel):
    ok: bool
    message: str
    count_checked: int
    bad_ids: Optional[list] = None