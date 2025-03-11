from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
# from sqlalchemy.ext.declarative import declarative_base
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todoapp.db'
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:mukhtar%408041@localhost/TodoApplicationDatabase' # %40 represent the @ symbol in SQLALCHEMY_DATABASE_URL
SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:mukhtar%408041@127.0.0.1:3306/TodoAppDatabase'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush= False,
    bind=engine
    )
Base = declarative_base()


