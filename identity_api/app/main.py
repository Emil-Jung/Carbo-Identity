"""
carbo-identity — standalone authentication & permissions service for the Carbo cloud.

People log in here (login_id + password) and receive a session token. Other
services (maintenance, quality) introspect that token via GET /auth/me and check
the returned permissions. Device keys remain per-platform for PWA writes only.
"""

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, auth, admin

app = FastAPI(
    title="Carbo Identity API",
    root_path="/identity/api",
    description="Central users, roles and permissions for the Carbo cloud",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, tags=["auth"])
app.include_router(admin.router, tags=["admin"])


@app.get("/")
def root():
    return {"service": "carbo-identity", "docs": "/docs"}
