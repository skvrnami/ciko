import time
import bleach
import pandas as pd
import numpy as np
import feedparser as fp
import trafilatura as tf

from datetime import datetime
from django.db.utils import IntegrityError
from ollama_summarise import summarise_text
from .models import Text
from .utils import bleach_text

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
    elif "updated_parsed" in df_entries.columns:
        df_entries["published"] = df_entries["updated_parsed"].apply(convert_date_parsed)
    elif "published" in df_entries.columns:
        df_entries["published"] = df_entries["published"].apply(convert_date)
    else:
        df_entries["published"] = datetime.today()

    missing_columns = set(required_columns) - set(df_entries.columns)

    for col in missing_columns:
        df_entries[col] = ""

    df_entries_trim = df_entries[required_columns]

    for _, row in df_entries_trim.iterrows():
        if row["content"] == "":
            try:
                html = tf.fetch_url(row["link"])
                txt = tf.extract(html, output_format = "html", include_links=True, 
                                 include_images=True, include_formatting=True, 
                                 include_comments=False)
            except:
                txt = row["summary"]
        # když je text krátký, zkus to scrapovat
        elif len(bleach_text(row["content"][0]["value"])) < 2000:
            try:
                html = tf.fetch_url(row["link"])
                txt = tf.extract(html, output_format = "html", include_links=True, 
                                 include_images=True, include_formatting=True, 
                                 include_comments=False)
            except:
                txt = row["summary"]
            
            if txt is None:
                txt = ""

            if len(row["content"][0]["value"]) > len(txt):
                txt = row["content"][0]["value"]
        
        elif len(row["content"][0]["value"]):
            txt = row["content"][0]["value"]
        else:
            try:
                html = tf.fetch_url(row["link"])
                txt = tf.extract(html, output_format = "html", include_links=True, include_images=True, include_formatting=True)
            except:
                txt = row["summary"]

        if len(row["summary"]) > 500:
            bleached_summary = bleach.clean(row["summary"], tags={'b', 'i'}, strip=True)
            row["summary"] = bleached_summary[0:500] + "[...]"
        
        t = Text(link = row["link"], publication_date = row["published"], author = row["author"], 
                 title = row["title"], summary = row["summary"], content = txt, source = feed.name)
        try:
            print(t)
            t.save()
        except IntegrityError:
            print("oops ", row["title"], " is already in the DB")
        
    
    return datetime.now()

def parse_link(url):
    try:
        html = tf.fetch_url(url)
        txt = tf.extract(html, output_format = "html", include_links=True, include_images=True, include_formatting=True)
        metadata = tf.extract_metadata(html).as_dict()
        summary = summarise_text(txt)
    except:
        try:
            txt = tf.extract(html, output_format = "html", include_images=True)
            if html is not None:
                metadata = tf.extract_metadata(html).as_dict()
                summary = summarise_text(txt)
            else:
                pass
        except:
            txt = tf.extract(html)
            metadata = tf.extract_metadata(html).as_dict()
            summary = summarise_text(txt)

    if txt is None:
        print("No text found")
        pass
    else:
        if metadata is not None:
            if "author" not in metadata.keys():
                metadata["author"] = "NA"
        if metadata is None:
            metadata["author"] = "NA"
            metadata["sitename"] = "NA"

        if metadata["author"] is None:
            metadata["author"] = "NA"

        t = Text(link = url, publication_date = metadata["date"], author = metadata["author"], title = metadata["title"], 
                 summary = summary, content = txt, source = metadata["sitename"])
            
        try:
            print(t)
            t.save()
        except IntegrityError as e:
            print(e)
            print("oops ", url, " is already in the DB")
    
    return datetime.now()

# def parse_pocket(last_updated)