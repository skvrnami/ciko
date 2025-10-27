import json
from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.template import loader
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from .models import Text, Highlight, RssFeed
from .stats import summarise_read_articles, graph_last_30_days
from .parsers import parse_feed, parse_link
from .utils import estimate_reading_time, bleach_text

def index(request):
    # Get the selected source from query parameters (for filtering)
    selected_source = request.GET.get('source')
    
    # Base queryset
    base_query = Text.objects.filter(~Q(read=True) & ~Q(deleted=True))
    
    # Calculate counts per source
    source_counts = base_query.values('source').annotate(
        count=Count('id')
    ).order_by('source')
    
    # Apply source filter if selected
    if selected_source:
        latest_texts = base_query.filter(source=selected_source)
    else:
        latest_texts = base_query
    
    # Order by publication date
    latest_texts = latest_texts.order_by("-publication_date")

    # Calculate reading time
    for text in latest_texts:
        text.reading_time = estimate_reading_time(bleach_text(text.content))

    page_number = request.GET.get('page', 1)
    paginator = Paginator(latest_texts, 10)
    try:
        texts = paginator.get_page(page_number)
    except Http404:
        texts = None

    context = {
        "latest_texts": texts,
        "source_counts": source_counts,
        "selected_source": selected_source,
    }

    return render(request, "read/index.html", context)

def archive(request):
    selected_source = request.GET.get('source')
    base_query = Text.objects.filter(Q(read=True)).order_by("-read_date")
    source_counts = base_query.values('source').annotate(
        count=Count('id')
    ).order_by('source')
    
    if selected_source:
        latest_texts = base_query.filter(source=selected_source)
    else:
        latest_texts = base_query
    
    latest_texts = latest_texts.order_by("-publication_date")

    for text in latest_texts:
        text.reading_time = estimate_reading_time(bleach_text(text.content))

    page_number = request.GET.get('page', 1)
    paginator = Paginator(latest_texts, 10)
    try:
        texts = paginator.get_page(page_number)
    except Http404:
        texts = None

    context = {
        "latest_texts": texts,
        "source_counts": source_counts,
        "selected_source": selected_source,
    }

    return render(request, "read/archive.html", context)

def trash(request):
    trashed_texts = Text.objects.filter(Q(deleted=True)).order_by("-id")
    page_number = request.GET.get('page', 1)
    paginator = Paginator(trashed_texts, 10)
    try:
        texts = paginator.get_page(page_number)
    except Http404:
        texts = None

    return render(request, "read/index.html", {"latest_texts": texts})

def detail(request, text_id):
    try:
        text = Text.objects.get(pk=text_id)
    except Text.DoesNotExist:
        raise Http404("Text does not exist")
    return render(request, "read/detail.html", {"text": text})

def read(request, text_id):
    t = get_object_or_404(Text, pk=text_id)
    t.read = not t.read
    t.read_date = t.read_date = now() if t.read else None
    t.save()

    if 'article' in request.META.get('HTTP_REFERER'):
        return redirect('index')
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def deleted(request, text_id):
    t = get_object_or_404(Text, pk=text_id)
    t.deleted = not t.deleted
    t.save()

    if 'article' in request.META.get('HTTP_REFERER'):
        return redirect('index')
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def stats(request):
    read_texts = Text.objects.filter(Q(read=True))
    df = summarise_read_articles(read_texts)
    avg = round(df["content_length_ns"].mean(), 1)
    data = graph_last_30_days(read_texts)
    chart_data = {
        'labels': data['date'].tolist(),
        'values': data['sum_ns'].tolist()
    }

    return render(request, "read/stats.html", {'data': json.dumps(chart_data, default=str), 'average': avg})

def highlights(request):
    hs = Highlight.objects.select_related('text').all().order_by("-created_at")

    return render(request, "read/highlights.html", {"highlights": hs})

def feeds(request):
    feeds = RssFeed.objects.all().order_by("-should_update", "name")

    return render(request, "read/feeds.html", {"feeds": feeds})

def update_feed(request, feed_id):
    feed = RssFeed.objects.filter(Q(id=feed_id))[0]
    updated = parse_feed(feed)
    RssFeed.objects.filter(Q(id=feed_id)).update(last_updated=updated)

    return redirect("index")

def update_feeds(request):
    feeds = RssFeed.objects.filter(should_update=True)
    for feed in feeds:
        updated = parse_feed(feed)
        RssFeed.objects.filter(Q(id=feed.id)).update(last_updated=updated)

    return redirect("index")

def change_feed_updates(request, feed_id):
    feed = RssFeed.objects.filter(Q(id=feed_id))[0]
    feed.should_update = not feed.should_update
    feed.save()

    return redirect("feeds")

@csrf_exempt
def save_link(request):
    if request.method == "POST":
        data = json.loads(request.body)
        url = data.get("url")
        print(url)
        parsed_link = parse_link(url)    

    return redirect("index")

@csrf_exempt
def add_highlight(request, text_id):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")
        print(content)
        text = get_object_or_404(Text, id=text_id)

        if content:
            highlight = Highlight.objects.create(text=text, content=content)
            return JsonResponse({'status': 'success', 'highlight_id': highlight.id, 'message': 'Highlight saved.'})

        return JsonResponse({'status': 'error', 'message': 'No content provided.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
