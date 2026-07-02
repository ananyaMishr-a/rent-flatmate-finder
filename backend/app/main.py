from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth_router

app = FastAPI(title="Rent & Flatmate Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend URL before final submission
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)

@app.get("/")
def root():
    return {"message": "Rent & Flatmate Finder API is running"}