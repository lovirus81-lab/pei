import asyncio
from sqlalchemy import delete
from app.database import SessionLocal
from app.models import Rule, Ruleset, Run

async def clean():
    async with SessionLocal() as db:
        await db.execute(delete(Run))
        await db.execute(delete(Rule))
        await db.execute(delete(Ruleset))
        await db.commit()
        print("Cleaned database")

if __name__ == "__main__":
    asyncio.run(clean())
