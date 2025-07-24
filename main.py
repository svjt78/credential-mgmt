# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models  # ensures models are registered
from routes import auth as auth_routes
from routes import oauth as oauth_routes

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Credential Management Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:3000"],  # Adjust/add if you have multiple origins
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # or list specific methods, e.g. ["GET", "POST"]
    allow_headers=["*"],  # or list specific headers
)

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(oauth_routes.router, tags=["oauth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Credential Management Service"}
