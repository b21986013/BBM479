from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas

def create_news(db: Session, news: schemas.NewsCreate):
    db_news = models.News(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

def get_all_news(db: Session, limit: int = 100):
    return (
        db.query(models.News)
        .order_by(models.News.published_at.desc())
        .limit(limit)
        .all()
    )

def get_news_by_category(db: Session, category: str):
    return (
        db.query(models.News)
        .filter(models.News.category == category)
        .order_by(models.News.published_at.desc())
        .all()
    )

def get_news_by_source(db: Session, source: str):
    return (
        db.query(models.News)
        .filter(models.News.source == source)
        .order_by(models.News.published_at.desc())
        .all()
    )

def get_news_paginated(db: Session, skip: int = 0, limit: int = 20):
    return (
        db.query(models.News)
        .order_by(models.News.published_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def search_news(db: Session, query: str):
    return (
        db.query(models.News)
        .filter(
            or_(
                models.News.title.ilike(f"%{query}%"),
                models.News.summary.ilike(f"%{query}%")
            )
        )
        .order_by(models.News.published_at.desc())
        .all()
    )

def get_distinct_categories(db: Session):
    rows = db.query(models.News.category).distinct().all()
    return [row[0] for row in rows if row[0] is not None]

def get_distinct_sources(db: Session):
    rows = db.query(models.News.source).distinct().all()
    return [row[0] for row in rows if row[0] is not None]

def get_news_by_id(db: Session, news_id: int):
    return (
        db.query(models.News)
        .filter(models.News.id == news_id)
        .first()
    )