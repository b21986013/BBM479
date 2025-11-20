from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    summary = Column(Text)
    url = Column(String, unique=True)
    category = Column(String)
    source = Column(String)
    image_url = Column(String, nullable=True)
    published_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
