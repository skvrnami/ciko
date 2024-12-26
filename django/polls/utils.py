import math
import bleach

def bleach_text(x):
    return bleach.clean(x, strip=True)

def estimate_reading_time(content, wpm=200):
    word_count = len(content.split())
    reading_time = math.ceil(word_count / wpm) 
    return reading_time