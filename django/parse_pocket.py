import os
import pandas as pd
import pocket as pckt
import datetime as dt
import trafilatura as tf
import django
from dotenv import load_dotenv

from django.db.utils import IntegrityError
from ollama_summarise import summarise_text

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

load_dotenv()

from read.models import Text

def convert_timestamp_to_date(x):
    d = dt.datetime.fromtimestamp(int(x), dt.UTC) 
    return d.strftime("%Y-%m-%dT%H:%M:%S+00:00")

p = pckt.Pocket(
    consumer_key = os.getenv("POCKET_CONSUMER_KEY"),
    access_token = os.getenv("POCKET_ACCESS_TOKEN")
)

pckt_articles = p.retrieve(count=10, state="unread")
pckt_articles_df = pd.DataFrame.from_dict(pckt_articles["list"], orient = "index")

pckt_articles_df["published"] = pckt_articles_df["time_added"].apply(convert_timestamp_to_date)
pckt_articles_df = pckt_articles_df.rename(columns = {"resolved_url":"link", "resolved_title":"title", "excerpt":"summary"})
pckt_articles_df_trim = pckt_articles_df[["published", "link", "title", "summary", "item_id"]]

for _, row in pckt_articles_df_trim.iterrows():
    print(row["title"])
    metadata = {}
    try:
        html = tf.fetch_url(row["link"])
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

        t = Text(link = row["link"], publication_date = row["published"], author = metadata["author"], title = row["title"], 
                summary = summary, content = txt, source = metadata["sitename"])
            
        try:
            print(t)
            t.save()
            p.archive(row["item_id"]).commit()
        except IntegrityError as e:
            print(e)
            print("oops ", row["title"], " is already in the DB")
            p.archive(row["item_id"]).commit()

