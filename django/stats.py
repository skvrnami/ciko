import os
import django
import pandas as pd


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db.models import Q
from polls.models import Text

read_texts = Text.objects.filter(Q(read=True))
read_texts.values("read_date", "content")
df = pd.DataFrame(
    list(
        read_texts.values(
            "title", "read_date", "content"
        )
    )
)

df['date'] = df['datetime'].dt.date
summary = df.groupby('date').agg(
    count_articles=('date', 'size'),  # Count the number of rows for each day
    content_length_ns=('content', lambda x: x.str.len().sum() / 1800)  # Sum of content lengths
).reset_index()