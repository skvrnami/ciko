import json
from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from .models import Text, Highlight
from .stats import summarise_read_articles

def index(request):
    latest_texts = Text.objects.filter(~Q(read=True) & ~Q(deleted=True)).order_by("-publication_date")[:10]
    template = loader.get_template("polls/index.html")
    context = {
        "latest_texts": latest_texts,
    }
    return render(request, "polls/index.html", context)

def archive(request):
    archived_texts = Text.objects.filter(Q(read=True)).order_by("-id")
    template = loader.get_template("polls/index.html")
    context = {
        "latest_texts": archived_texts,
    }
    return render(request, "polls/index.html", context)

def trash(request):
    trashed_texts = Text.objects.filter(Q(deleted=True)).order_by("-id")
    template = loader.get_template("polls/index.html")
    context = {
        "latest_texts": trashed_texts,
    }
    return render(request, "polls/index.html", context)

def detail(request, text_id):
    try:
        text = Text.objects.get(pk=text_id)
    except Text.DoesNotExist:
        raise Http404("Text does not exist")
    return render(request, "polls/detail.html", {"text": text})

def read(request, text_id):
    t = get_object_or_404(Text, pk=text_id)
    t.read = not t.read
    t.read_date = t.read_date = now() if t.read else None
    t.save()

    return redirect("index")

def deleted(request, text_id):
    t = get_object_or_404(Text, pk=text_id)
    t.deleted = not t.deleted
    t.save()

    return redirect("index")

def stats(request):
    read_texts = Text.objects.filter(Q(read=True))
    df = summarise_read_articles(read_texts)
    df_html = df.to_html(classes='table table-striped table-bordered')

    return render(request, "polls/stats.html", {'df_html': df_html})

def highlights(request):
    hs = Highlight.objects.select_related('text').all().order_by("-created_at")

    return render(request, "polls/highlights.html", {"highlights": hs})

@csrf_exempt
def add_highlight(request, text_id):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")
        print(content)
        # content = request.POST.get('content')  # Get the selected text from the POST data
        text = get_object_or_404(Text, id=text_id)

        # Save the highlight in the database
        if content:
            highlight = Highlight.objects.create(text=text, content=content)
            return JsonResponse({'status': 'success', 'highlight_id': highlight.id, 'content': content})

        return JsonResponse({'status': 'error', 'message': 'No content provided.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
