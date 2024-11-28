import time
import pandas as pd
import numpy as np
import feedparser as fp
import trafilatura as tf

from datetime import datetime
from django.db.utils import IntegrityError
from .models import Text
from ollama_summarise import summarise_text

def convert_date(x):
    try:
        # Parse the string into a datetime object
        dt = datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %Z")
        # Convert to the desired ISO 8601 format
        return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    except:
        # Handle cases where the date string is not in the expected format
        return datetime.now()

def convert_date_parsed(x):
    return datetime.fromtimestamp(time.mktime(x))

def parse_feed(feed):
    feed_entries = fp.parse(feed.url)
    entries = feed_entries.entries
    df_entries = pd.DataFrame.from_dict(entries)

    required_columns = ["published", "title", "summary", "author", "link", "content"]  

    if "published_parsed" in df_entries.columns:
        df_entries["published"] = df_entries["published_parsed"].apply(convert_date_parsed)
    else:
        df_entries_trim["published"] = df_entries_trim["published"].apply(convert_date)

    missing_columns = set(required_columns) - set(df_entries.columns)

    for col in missing_columns:
        df_entries[col] = ""

    df_entries_trim = df_entries[required_columns]

    for _, row in df_entries_trim.iterrows():
        if len(row["content"][0]["value"]):
            txt = row["content"][0]["value"]
        else:
            try:
                html = tf.fetch_url(row["link"])
                txt = tf.extract(html, output_format = "html", include_links=True, include_images=True, include_formatting=True)
            except:
                txt = row["summary"]

        if len(row["summary"]) > 500:
            row["summary"] = row["summary"][0:500] + "[...]"
        
        t = Text(link = row["link"], publication_date = row["published"], author = row["author"], 
                 title = row["title"], summary = row["summary"], content = txt, source = feed.name)
        try:
            print(t)
            t.save()
        except IntegrityError:
            print("oops ", row["title"], " is already in the DB")
        
    
    return datetime.now()