from fastapi import FastAPI, Depends
from database import Base, engine, get_db, SessionLocal
from apscheduler.schedulers.background import BackgroundScheduler
from routers import news, sources
from crawler.rss_reader import run_all_rss_readers
from datetime import datetime, timedelta
import uvicorn

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="News Aggregation API",
    description="Multi-source news collector backend",
    version="1.0.0"
)

scheduler = BackgroundScheduler()

app.include_router(news.router)
# app.include_router(sources.router)

@app.get("/")
def root():
    return {"message": "News Aggregation Backend is running!"}

def scheduled_rss_job():
    print("[*] Scheduled RSS Job Working…\n")

    db = SessionLocal()
    try:
        run_all_rss_readers(db)
    finally:
        db.close()

    print("[✓] Scheduled RSS Job Finished.")

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(
        func=scheduled_rss_job,
        trigger="interval",
        minutes=5,
        id="rss_crawler_job",
        replace_existing=True,
        next_run_time=datetime.now() + timedelta(seconds=3) 
    )
    scheduler.start()

# Uygulamayı localhost üzerinde başlat
if __name__ == "__main__" :
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)