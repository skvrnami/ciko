import pandas as pd

from .utils import bleach_text

def summarise_read_articles(read_texts):
    df = pd.DataFrame(
    list(
        read_texts.values(
            "title", "read_date", "content"
        )
    )
    )

    df['date'] = df['read_date'].dt.date
    df['sanitized_content'] = df['content'].apply(lambda x: bleach_text(x))
    summary = df.groupby('date').agg(
        count_articles=('date', 'size'),  # Count the number of rows for each day
        content_length_ns=('sanitized_content', lambda x: round(x.str.len().sum() / 1800, 1))  # Sum of content lengths
    ).reset_index()

    return summary