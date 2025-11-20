from pydantic import BaseModel
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    summary: str | None = None
    url: str
    category: str | None = None
    source: str
    image_url: str | None = None
    published_at: datetime | None = None

class NewsCreate(NewsBase):
    pass

class NewsOut(NewsBase):
    id: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }
