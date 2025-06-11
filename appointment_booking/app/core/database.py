from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from config import settings

engine = create_engine(settings.POSTGRES_DB)
SessionLocal = sessionmaker(autoflush=False, autocommit=False,bind=engine)
Base = declarative_base()
