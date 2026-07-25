from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from routers.auth import router as auth_router
from routers.prescription import router as prescription_router
from routers.pharmacy import router as pharmacy_router
from routers.orders import router as orders_router
from routers.search import router as search_router

app = FastAPI(title="MediLink Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(prescription_router)
app.include_router(pharmacy_router)
app.include_router(orders_router)
app.include_router(search_router)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
def home():
    return {"project": "MediLink", "status": "Online", "message": "Backend is running with Auth Module"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)