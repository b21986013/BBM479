from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import crud, schemas

router = APIRouter(prefix="/news", tags=["News"])

@router.get("/", response_model=list[schemas.NewsOut])
def get_news(db: Session = Depends(get_db)):
    return crud.get_all_news(db)

@router.get("/category/{category}", response_model=list[schemas.NewsOut])
def get_news_by_category(category: str, db: Session = Depends(get_db)):
    return crud.get_news_by_category(db, category)
