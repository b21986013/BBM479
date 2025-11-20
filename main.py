from fastapi import FastAPI, Depends
from database import Base, engine, get_db
from sqlalchemy.orm import Session
from routers import news, sources
from crawler.rss_reader import run_all_rss_readers
import uvicorn

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="News Aggregation API",
    description="Multi-source news collector backend",
    version="1.0.0"
)

# Routerları ekle
app.include_router(news.router)
# app.include_router(sources.router)

@app.get("/")
def root():
    return {"message": "News Aggregation Backend is running!"}

@app.get("/run-crawler")
def run_crawler(db: Session = Depends(get_db)):
    run_all_rss_readers(db)
    return {"message": "Crawler çalıştı"}


# Uygulamayı localhost üzerinde başlat
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)