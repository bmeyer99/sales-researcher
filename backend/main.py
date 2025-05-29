from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware  # Added for CORS
from api.v1.auth import router as auth_router
from api.v1.research import router as research_router
from core.config import settings

app = FastAPI(
    title="Sales Prospect Research Tool API",
    description="API for managing sales prospect research tasks.",
    version="0.1.0",
)

# Add SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.FRONTEND_URL)],  # Allows only the frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include API routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(research_router, prefix="/api/research", tags=["Research"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Sales Prospect Research Tool API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Further endpoints will be added in subsequent tasks.
