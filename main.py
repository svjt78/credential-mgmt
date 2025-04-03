# main.py
from fastapi import FastAPI
from database import engine, Base
import models  # ensures models are registered
from routes import auth as auth_routes
from routes import oauth as oauth_routes

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Credential Management Service")

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(oauth_routes.router, tags=["oauth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Credential Management Service"}
