from fastapi import FastAPI
from database import engine,Base
from Routers import auth,tasks
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from core.rate_limit import limiter
from fastapi.middleware.cors import CORSMiddleware
import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Driven Smart Task & Calendar Automator",
    description="A production-ready API for natural language task parsing and management.",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)



app.include_router(auth.router)
app.include_router(tasks.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "online", "message": "Welcome to the AI Task Automator API"}