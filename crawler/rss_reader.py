import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
import crud, schemas, models
import requests
import xml.etree.ElementTree as ET

RSS_SOURCES = [
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/turkiye/news",
        "default_category": "turkiye"
    },
     {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/turkiye_articles.rss",
        "default_category": "turkiye"
    },
    {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/dunya/news",
        "default_category": "dunya"
    },
    {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/dunya_articles.rss",
        "default_category": "dunya"
    },
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/kultur-sanat/news",
        "default_category": "kultur-sanat"
    },
     {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/kultur_sanat_articles.rss",
        "default_category": "kultur-sanat"
    },
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/bilim-teknoloji/news",
        "default_category": "bilim-teknoloji"
    },
    {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/bilim_teknoloji_articles.rss",
        "default_category": "bilim-teknoloji"
    },
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/yasam/news",
        "default_category": "yasam"
    },
     {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/yasam_articles.rss",
        "default_category": "yasam"
    },
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/magazin/news",
        "default_category": "magazin"
    },
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/saglik/news",
        "default_category": "saglik"
    },
  
     {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/saglik_articles.rss",
        "default_category": "saglik"
    },
     {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/ekonomi_articles.rss",
        "default_category": "ekonomi"
    },
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/ekonomi/news",
        "default_category": "ekonomi"
    },
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/otomobil/news",
        "default_category": "otomobil"
    },
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/seyahat/news",
        "default_category": "seyahat"
    },
   
     {
        "name": "CNN Türk",
        "url": "https://www.cnnturk.com/feed/rss/spor/news",
        "default_category": "spor"
    },
     {
        "name": "TRT Haber",
        "url": "https://www.trthaber.com/spor_articles.rss",
        "default_category": "spor"
    },
 
]

def extract_image_from_item_xml(rss_url, link):
    try:
        res = requests.get(rss_url, timeout=5)
        root = ET.fromstring(res.content)

        for item in root.findall(".//item"):
            item_link = item.find("link")
            if item_link is not None and item_link.text == link:
                img = item.find("image")
                if img is not None and img.text:
                    return img.text
        return None

    except Exception:
        return None

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


def extract_image(entry, rss_url=None):
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    
    if 'media_thumbnail' in entry:
        return entry.media_thumbnail[0]['url']
    
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0]['href']
    
    if entry.get("image"):
        return entry.get("image")

    # summary’den çekmeyi dene
    if entry.get("summary"):
        url = extract_image_from_description(entry["summary"])
        if url:
            return url

    # 🔥 CNN Türk özel fallback (image tag’i sadece XML’de)
    if rss_url and "cnnturk" in rss_url:
        return extract_image_from_item_xml(rss_url, entry.get("link"))

    return None

def parse_rss_feed(db: Session, source_name: str, rss_url: str, default_category: str):
    print(f"[*] Reading RSS feed: {source_name} - {default_category}")

    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
 

        title = entry.get("title")
        link = entry.get("link")
        if not title or not link:
            continue
       
        summary = entry.get("summary")   
        image_url = extract_image(entry, rss_url=rss_url)
       
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

    print(f"[✓] {source_name} - {default_category} RSS okuma tamamlandı.\n")



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
