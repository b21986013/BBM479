import feedparser
from datetime import datetime
from sqlalchemy.orm import Session
import crud, schemas, models

# Örnek RSS kaynakları — istediğin gibi çoğaltabilirsin
RSS_SOURCES = [
    {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/rss/tumhaber.rss",
        "default_category": "general"
    },
    {
        "name": "NTV",
        "url": "https://www.ntv.com.tr/son-dakika.rss",
        "default_category": "general"
    },
]


def parse_rss_feed(db: Session, source_name: str, rss_url: str, default_category: str):
    """
    Tek bir RSS feed'ini okur ve veritabanına kaydeder.
    """
    print(f"[*] Reading RSS feed: {source_name}")

    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        title = entry.get("title", None)
        link = entry.get("link", None)
        summary = entry.get("summary", None)

        # Zorunlu alan kontrolü
        if not title or not link:
            continue

        # Yayın tarihi varsa al
        published_at = None
        if hasattr(entry, "published"):
            try:
                published_at = datetime(*entry.published_parsed[:6])
            except:
                pass

        # Duplicate kontrol: URL eşsiz olmalı
        existing = db.query(models.News).filter(models.News.url == link).first()
        if existing:
            continue

        # Kaydedilecek haber objesi
        news_obj = schemas.NewsCreate(
            title=title,
            summary=summary,
            url=link,
            category=default_category,
            source=source_name,
            image_url=None,  # RSS'ten gelmiyorsa sonra eklenebilir
            published_at=published_at,
        )

        crud.create_news(db, news_obj)

    print(f"[✓] {source_name} RSS okuma tamamlandı.\n")


def run_all_rss_readers(db: Session):
    """
    Tüm RSS kaynaklarını sırayla okur.
    """
    print("=== RSS Reader Started ===")

    for source in RSS_SOURCES:
        parse_rss_feed(
            db=db,
            source_name=source["name"],
            rss_url=source["url"],
            default_category=source["default_category"]
        )

    print("=== RSS Reader Finished ===\n")
