from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Healthcare App API",
    description="Backend for blood report AI analysis",
    version="1.0.0"
)

# CORS (safe dev + future frontend flexibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (better than root-only testing)
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Backend is running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
