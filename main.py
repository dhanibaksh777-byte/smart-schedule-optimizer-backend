from fastapi import FastAPI
from database import engine,Base
from Routers import auth,tasks
import models
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Driven Smart Task & Calendar Automator",
    description="A production-ready API for natural language task parsing and management.",
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(tasks.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-gse2.vercel.app/"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "online", "message": "Welcome to the AI Task Automator API"}