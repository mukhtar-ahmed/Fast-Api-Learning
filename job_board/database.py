from config import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


settings = Settings()

engine = create_engine(settings.database_url, connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


