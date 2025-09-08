from fastapi import FastAPI
from .middleware import install_middleware
from .routers.skills import router as skills_router

app = FastAPI(title="MindForge Backend", version="0.1.0")

# middleware (CORS, timing headers, etc.)
install_middleware(app)

# health
@app.get("/health", tags=["_meta"])
def health():
    return {"status": "ok"}

# api routes
app.include_router(skills_router, prefix="/api")
