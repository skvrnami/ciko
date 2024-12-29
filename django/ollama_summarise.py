import os
import django
from ollama import chat

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from read.models import Text

texts = Text.objects.order_by("-id")

def summarise_text(text, model="llama3"):
    response = chat(model=model, messages=[
    {
        'role': 'user',
        'content': "Summarise the key points of the following article, be as concise as possible. The text is the following: " + text
    },
    ])

    return response.message.content

