
import asyncio
from app.database import engine
from app.models.user import Base as UserBase
from app.models.job import Base as JobBase
from app.models.candidate import Base as CandidateBase
from app.utils.esco import build_local_taxonomy_cache

async def init_db():
    print("=> Creating all tables in Postgres...")
    # Import all models to ensure they are registered with Base metadata
    import app.models.user
    import app.models.job
    import app.models.candidate
    import app.models.matching
    import app.models.outcome
    
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    print("=> Database schema initialized.")
    
    print("=> Building ESCO local taxonomy cache...")
    await build_local_taxonomy_cache()
    print("=> Taxonomy cache built.")

if __name__ == "__main__":
    asyncio.run(init_db())
