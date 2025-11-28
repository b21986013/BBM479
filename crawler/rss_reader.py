import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
import crud, schemas, models

RSS_SOURCES = [
    {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/manset_articles.rss",
        "default_category": "manşet"
    },
    {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/all/news",
        "default_category": "manşet"
    },
]

def extract_image_from_description(html: str) -> str | None:
    """
    RSS <description> içerisindeki HTML'den <img src="..."> URL'sini çıkarır.
    """
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]
    
    return None


def extract_image(entry):
    if 'media_content' in entry:
        image_url = entry.media_content[0]['url']
        return image_url
    
    elif 'media_thumbnail' in entry:
        image_url = entry.media_thumbnail[0]['url']
        return image_url
    
    elif 'enclosures' in entry and len(entry.enclosures) > 0:
        image_url = entry.enclosures[0]['href']
        return image_url
    
    if entry.get("image"):
        return entry.get("image")

    if entry.get("summary"):
        url = extract_image_from_description(entry["summary"])
        if url:
            return url

    return None

def parse_rss_feed(db: Session, source_name: str, rss_url: str, default_category: str):
    print(f"[*] Reading RSS feed: {source_name}")

    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        title = entry.get("title")
        link = entry.get("link")
        if not title or not link:
            continue
       
        summary = entry.get("summary")   
        image_url = extract_image(entry)
       
        published_at = None
        if hasattr(entry, "published"):
            try:
                published_at = datetime(*entry.published_parsed[:6])
            except:
                pass

        # Duplicate kontrol
        existing = db.query(models.News).filter(models.News.url == link).first()
        if existing:
            continue

        news_obj = schemas.NewsCreate(
            title=title,
            summary=summary,
            url=link,
            category=default_category,
            source=source_name,
            image_url=image_url,
            published_at=published_at,
        )

        crud.create_news(db, news_obj)

    print(f"[✓] {source_name} RSS okuma tamamlandı.\n")



def run_all_rss_readers(db: Session):
    """
    Tüm RSS kaynaklarını sırayla okur.
    """
    for source in RSS_SOURCES:
        parse_rss_feed(
            db=db,
            source_name=source["name"],
            rss_url=source["url"],
            default_category=source["default_category"]
        )
