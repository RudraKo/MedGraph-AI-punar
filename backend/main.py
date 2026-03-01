from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from backend.routers import auth, drugs, interactions, prescriptions, schedules, alerts, scan

load_dotenv()

app = FastAPI(title="MedGraph.AI API", version="1.0.0")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(drugs.router, prefix="/api/v1")
app.include_router(interactions.router, prefix="/api/v1")
app.include_router(prescriptions.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "MedGraph.AI API Running"}
