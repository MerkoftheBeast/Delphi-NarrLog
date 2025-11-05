import json, hashlib
from typing import Optional, Dict, Any

def cannonical_payload(author: str, 
                       body: str, 
                       node_code: Optional[int], 
                       input_code: Optional[int], 
                       tags: Optional[Dict[str, Any]], 
                       supersedes_id: Optional[int]) -> str:
    data = {
        "author": author,
        "body": body,
        "node_code": node_code,
        "input_code": input_code,
        "tags": tags or {},
        "supersedes_id": supersedes_id
    }

    return json.dumps(data, separators=(",", ":"), sort_keys=True, ensure_ascii=False)

def chain_hash(prev_hash: Optional[str], payload: str) -> str:
    h = hashlib.sha256()
    h.update((prev_hash or "").encode("utf-8"))
    h.update(payload.encode("utf-8"))
    return h.hexdigest()