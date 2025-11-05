from fastapi import Header

async def current_user(x_user: str = Header(default="unknown")) -> str:
    return x_user or "unknown"