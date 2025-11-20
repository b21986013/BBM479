from sqlalchemy.orm import Session
import models, schemas

def create_news(db: Session, news: schemas.NewsCreate):
    db_news = models.News(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

def get_all_news(db: Session, limit=100):
    return db.query(models.News).order_by(models.News.published_at.desc()).limit(limit).all()

def get_news_by_category(db: Session, category: str):
    return db.query(models.News).filter(models.News.category == category).all()
