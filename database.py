from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("database_url")
if not DATABASE_URL:
    raise RuntimeError("CRITICAL ERROR : database url does'nt exists in .env file")

engine = create_engine(DATABASE_URL,pool_size=20,max_overflow=10,pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind = engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()