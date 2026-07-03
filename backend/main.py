# pyrefly: ignore [missing-import]
from app.main import app

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Kavalar Behavioral Anomaly Detector Backend"
    }

@app.get("/health")
def health():
    """
    Root level health redirect/alias.
    """
    return {
        "status": "healthy"
    }
