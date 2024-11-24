import sqlite3
import pandas as pd
import feedparser as fp
import trafilatura as tf
from datetime import datetime

rss_feeds = ["https://www.theverge.com/rss/index.xml", 
             "https://simonwillison.net/atom/everything/", 
             "https://www.hearingthings.co/archive/rss/", 
             "https://www.citationneeded.news/rss/"]

def convert_date(x):
    try:
        # Parse the string into a datetime object
        dt = datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %Z")
        # Convert to the desired ISO 8601 format
        return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    except ValueError:
        # Handle cases where the date string is not in the expected format
        return x

entries = []
for feed in rss_feeds:
    feed_entries = fp.parse(feed)
    entries = entries + feed_entries.entries

df_entries = pd.DataFrame.from_dict(entries)
df_entries_trim = df_entries[["published", "title", 
    "summary", "author", "link"
]]
df_entries_trim["published"] = df_entries_trim["published"].apply(convert_date)

conn = sqlite3.connect("test.db")

with conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS texts (
        id INTEGER PRIMARY KEY,
        published TEXT,
        link TEXT UNIQUE,
        author TEXT,
        title TEXT,
        summary TEXT, 
        content TEXT
    )
    """)

for _, row in df_entries_trim.iterrows():
    try:
        html = tf.fetch_url(row["link"])
        txt = tf.extract(html)
    except:
        txt = "ERROR: did not fetched content from html"
    
    with conn:
        conn.execute("""
        INSERT OR IGNORE INTO texts (published, link, author, title, summary, content) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, (row["published"], row["link"], row["author"], row["title"], 
        row["summary"], txt))
    
result = pd.read_sql("SELECT * FROM texts", conn)
print(result)
