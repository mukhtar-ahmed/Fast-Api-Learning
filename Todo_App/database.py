from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
# from sqlalchemy.ext.declarative import declarative_base
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todoapp0.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush= False,
    bind=engine
    )
Base = declarative_base()


