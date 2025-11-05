import os
from typing import Optional, List
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from .log_db import Base, engine, get_db
from .log_models import LogEntry
from .log_schemas import LogCreate, LogOut, IntegrityReport
from .log_hashing import cannonical_payload, chain_hash
from .log_broadcast import manager
from .log_security import current_user

load_dotenv()

app = FastAPI(title="Delphi Narrative Log", version="0.1.0")

origins = (os.getenv("ALLOWED_ORIGINS") or "").split(",")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in origins if o.strip()],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

Base.metadata.create_all(bind=engine)

@app.get("/ping")
def ping():
    return {"status": "ok"}

def _latest_hash(db: Session) -> Optional[str]:
    stmt = select(LogEntry.curr_hash).order_by(desc(LogEntry.created_utc),
                                               desc(LogEntry.id)).limit(1)
    row = db.execute(stmt).first()
    return row[0] if row else None

def _to_out(m: LogEntry) -> LogOut:
    return LogOut(id=m.id, created_utc=m.created_utc.isoformat(), 
                  author=m.author,
                  body=m.body,
                  node_code=m.node_code,
                  input_code=m.input_code,
                  tags=m.tags or {},
                  supersedes_id=m.supersedes_id
                )

@app.post("/log", response_model=LogOut)
def create_log(payload: LogCreate, user:
               str = Depends(current_user), db: Session = Depends(get_db)):
               prev = _latest_hash(db)
               canon = cannonical_payload(author=user, body=payload.body,
                                          node_code=payload.node_code,
                                          input_code=payload.input_code,
                                          tags=payload.tags, 
                                          supersedes_id=None)
               curr = chain_hash(prev, canon)
               entry = LogEntry(
                      author=user, 
                      body=payload.body,
                      node_code=payload.node_code,
                      input_code=payload.input_code,
                      tags=payload.tags, 
                      supersedes_id=None,
               )
               db.add(entry)
               db.commit()
               db.refresh(entry)
               out = _to_out(entry)
               #Websocket Broadcast
               import anyio
               anyio.from_thread.run(manager.broadcast, {"type": "edited", "entry": out.dict()})

@app.get("/log", response_model=List[LogOut])
def list_logs(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
       stmt = select(LogEntry).order_by(desc(LogEntry.created_utc),
                                        desc(LogEntry.id)).limit(limit)
       rows = db.execute(stmt).scalars().all()
       return [_to_out(r) for r in rows]

@app.get("/log/{log_id}", response_model=LogOut)
def get_log(log_id: int, db: Session = Depends(get_db)):
       m = db.get(LogEntry, log_id)
       if not m:
              raise HTTPException(status_code=404, detail="log not found")
       return _to_out(m)

@app.get("/integrity", response_model=IntegrityReport)
def integrity_check(db: Session = Depends(get_db)):
       # Verify the chain in chronological order
       stmt = select(LogEntry).order_by(LogEntry.created_utc, LogEntry.id)
       rows = db.execute(stmt).scalars().all()
       prev = None
       bad = []
       for r in rows:
            expected = chain_hash(prev, cannonical_payload(r.author, 
                                                             r.body, 
                                                             r.node_code, 
                                                             r.input_code, 
                                                             r.tags, 
                                                             r.supersedes_id))
            if r.prev_hash != prev or r.curr != expected:
                bad.append(r.id)
            prev = r.curr_hash
        
       if bad:
             return IntegrityReport(ok=False, message="chain breaks detected",
                                    count_checked=len(rows), bad_ids=bad)
       return IntegrityReport(ok=True, message="Chain valid",
                              count_checked=len(rows))

@app.websocket("/stream")
async def stream(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
          manager.disconnect(ws)
    except Exception:
          manager.disconnect(ws)
    