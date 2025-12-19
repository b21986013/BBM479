from fastapi import FastAPI
from database import Base, engine, SessionLocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routers import news
from crawler.rss_reader import run_all_rss_readers
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import uvicorn

Base.metadata.create_all(bind=engine)

scheduler = AsyncIOScheduler()

def scheduled_rss_job():
    print("[*] Scheduled RSS Job Working…")

    db = SessionLocal()
    try:
        run_all_rss_readers(db)
    finally:
        db.close()

    print("[✓] Scheduled RSS Job Finished.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        func=scheduled_rss_job,
        trigger="interval",
        minutes=5,
        id="rss_crawler_job",
        replace_existing=True,
        next_run_time=datetime.utcnow() + timedelta(seconds=3)
    )
    scheduler.start()
    print("Scheduler started in Railway")
    yield
    scheduler.shutdown()
    print("Scheduler stopped")


app = FastAPI(
    title="News Aggregation API",
    description="Multi-source news collector backend",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(news.router)

@app.get("/")
def root():
    return {"message": "News Aggregation Backend is running with scheduler!"}

if __name__ == "__main__" :
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)