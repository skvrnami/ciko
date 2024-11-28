import bleach

def bleach_text(x):
    return bleach.clean(x, strip=True)
