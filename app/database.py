from sqlqlchemy import create_engine
from sqlqlchemy.orm import sessionmaker 
from sqlqlchemy.ext.declarative import declarative_base

URL_DATABASE = "postgresql://anton:hornetm3@localhost:5432/amur"

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind=engine)