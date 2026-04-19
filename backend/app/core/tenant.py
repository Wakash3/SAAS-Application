from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db, set_tenant
import httpx
from .config import settings


async def get_current_tenant(
    authorization: str = Header(...),
    x_branch_id: str = Header(None),
    db: Session = Depends(get_db),
) -> str:
    """
    Validates Clerk JWT and returns tenant_id (org ID).
    Sets RLS context on the DB session.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ")[1]

    # Verify with Clerk
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.clerk.com/v1/tokens/verify",
            headers={
                "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                "Content-Type": "application/json",
            },
            params={"token": token},
        )

    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    data = r.json()
    org_id = data.get("org_id") or data.get("sub")
    if not org_id:
        raise HTTPException(status_code=401, detail="No org context")

    set_tenant(db, org_id)
    return org_id