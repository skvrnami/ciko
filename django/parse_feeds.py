import os
import pandas as pd
import feedparser as fp
import trafilatura as tf
from datetime import datetime
import bleach 
from django.db.utils import IntegrityError

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from polls.models import Text


rss_feeds = ["https://www.theverge.com/rss/index.xml", 
             "https://simonwillison.net/atom/everything/", 
             "https://www.hearingthings.co/archive/rss/", 
             "https://www.citationneeded.news/rss/"]

rss_feeds = ["https://statmodeling.stat.columbia.edu/feed/"]


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

for _, row in df_entries_trim.iterrows():
    try:
        html = tf.fetch_url(row["link"])
        txt = tf.extract(html, output_format = "html", include_links=True, include_images=True, include_formatting=True)
    except:
        txt = "ERROR: did not fetched content from html"
    
    t = Text(link = row["link"], publication_date = row["published"], author = row["author"], title = row["title"], 
             summary = row["summary"], content = txt)
    try:
        t.save()
    except IntegrityError:
        print("oops ", row["title"], " is already in the DB")
