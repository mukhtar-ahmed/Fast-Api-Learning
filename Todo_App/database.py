from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
# from sqlalchemy.ext.declarative import declarative_base
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todo.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': True})
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush= False,
    bind=engine
    )
Base = declarative_base()


