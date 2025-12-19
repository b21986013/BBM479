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

@router.get("/search/", response_model=list[schemas.NewsOut])
def search_news(
    q: str,
    db: Session = Depends(get_db)
):
    return crud.search_news(db, q)

@router.get("/page/", response_model=list[schemas.NewsOut])
def get_news_paginated(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return crud.get_news_paginated(db, skip, limit)

@router.get("/source/{source}", response_model=list[schemas.NewsOut])
def get_news_by_source(source: str, db: Session = Depends(get_db)):
    return crud.get_news_by_source(db, source)

@router.get("/categories", response_model=list[str])
def get_categories(db: Session = Depends(get_db)):
    return crud.get_distinct_categories(db)

@router.get("/sources", response_model=list[str])
def get_sources(db: Session = Depends(get_db)):
    return crud.get_distinct_sources(db)

@router.get("/{news_id}", response_model=schemas.NewsOut)
def get_news_detail(news_id: int, db: Session = Depends(get_db)):
    return crud.get_news_by_id(db, news_id)