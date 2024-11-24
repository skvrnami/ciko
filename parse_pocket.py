import os
import pandas as pd
import pocket as pckt
import datetime as dt

def convert_timestamp_to_date(x):
    d = dt.datetime.fromtimestamp(int(x), dt.UTC) 
    return d.strftime("%Y-%m-%dT%H:%M:%S+00:00")

p = pckt.Pocket(
    consumer_key = os.environ["POCKET_CONSUMER_KEY"],
    access_token = os.environ["POCKET_ACCESS_TOKEN"]
)

pckt_articles = p.retrieve(count = 10)
pckt_articles_df = pd.DataFrame.from_dict(pckt_articles["list"], orient = "index")

pckt_articles_df["published"] = pckt_articles_df["time_added"].apply(convert_timestamp_to_date)
pckt_articles_df = pckt_articles_df.rename(columns = {"resolved_url":"link", "resolved_title":"title", "excerpt":"summary"})
pckt_articles_df_trim = pckt_articles_df[["published", "link", "title", "summary"]]

conn = sqlite3.connect("test.db")

for _, row in pckt_articles_df_trim.iterrows():
    try:
        html = tf.fetch_url(row["link"])
        txt = tf.extract(html)
        author = tf.extract_metadata(html).as_dict()["author"]
    except:
        txt = "ERROR: did not fetched content from html"
        author = ""
    
    with conn:
        conn.execute("""
        INSERT OR IGNORE INTO texts (published, link, author, title, summary, content) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, (row["published"], row["link"], author, row["title"], 
        row["summary"], txt))

conn.commit()
conn.close()
