# pyrefly: ignore [missing-import]
from fastapi import FastAPI

app = FastAPI(title="Sentinel AI")

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }