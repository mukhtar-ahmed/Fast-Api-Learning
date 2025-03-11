from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# For Postgress
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:mukhtar%408041@localhost/StoryDayDatabase"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# For SQLite3   
# SQLALCHEMY_DATABASE_URL = "sqlite:///./storyapp.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)
Base = declarative_base()