from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Float
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DSN


engine = create_async_engine(DSN)
Base = declarative_base(bind=engine)

class Pers(Base):
    __tablename__ = "pers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    films = Column(String, nullable=True)
    species = Column(String, nullable=True)
    starships = Column(String, nullable=True)
    vehicles = Column(String, nullable=True)

Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

