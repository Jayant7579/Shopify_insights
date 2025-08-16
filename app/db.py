
import os
import mysql.connector
from .models import BrandResponse

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST","localhost"),
        user=os.getenv("MYSQL_USER","root"),
        password=os.getenv("MYSQL_PASSWORD",""),
        database=os.getenv("MYSQL_DB","shopify_insights"),
    )

def init_schema():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS brands (
            id INT AUTO_INCREMENT PRIMARY KEY,
            website_url VARCHAR(255) UNIQUE,
            is_shopify_like BOOLEAN,
            about_brand TEXT,
            fetched_at VARCHAR(32)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS products (
            id BIGINT,
            website_url VARCHAR(255),
            title VARCHAR(255),
            handle VARCHAR(255),
            url TEXT,
            vendor VARCHAR(255),
            product_type VARCHAR(255),
            tags TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS faqs (
            website_url VARCHAR(255),
            question TEXT,
            answer TEXT
    )""")
    conn.commit()
    cur.close()
    conn.close()

def persist_brand_data(data: BrandResponse):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("REPLACE INTO brands (website_url,is_shopify_like,about_brand,fetched_at) VALUES (%s,%s,%s,%s)",
                (data.website_url, data.is_shopify_like, data.about_brand, data.fetched_at))
    for p in data.product_catalog:
        cur.execute("REPLACE INTO products (id,website_url,title,handle,url,vendor,product_type,tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (p.id, data.website_url, p.title, p.handle, p.url, p.vendor, p.product_type, p.tags))
    for f in data.faqs:
        cur.execute("INSERT INTO faqs (website_url,question,answer) VALUES (%s,%s,%s)",
                    (data.website_url, f.question, f.answer))
    conn.commit()
    cur.close()
    conn.close()
