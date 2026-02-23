from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.api import reference, projects, diagrams, validate, repair, generate

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: e.g. DB connection
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown

app = FastAPI(
    title="PEI Backend API",
    description="Plant Engineering IDE Backend",
    version="0.1.0",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reference.router)
app.include_router(projects.router)
app.include_router(diagrams.router)
app.include_router(validate.router)
app.include_router(repair.router)
app.include_router(generate.router)

@app.get("/")
async def root():
    return {"message": "Welcome to PEI API"}
