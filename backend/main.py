from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import ocr, interactions, scheduling

app = FastAPI(
    title="MedSync API",
    description="A graph-based polypharmacy safety and medication coordination platform.",
    version="1.0.0"
)

# Add CORS Middleware for the frontend application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Expand to explicit origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(ocr.router, prefix="/api/v1")
app.include_router(interactions.router, prefix="/api/v1")
app.include_router(scheduling.router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health_check():
    """Simple healthcheck for the MedSync API."""
    return {"status": "healthy", "service": "MedSync AI Gateway"}
