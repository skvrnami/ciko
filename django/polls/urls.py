from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("archive", views.archive, name="archive"),
    path("trash", views.trash, name="trash"),
    path("article/<int:text_id>/", views.detail, name="detail"),
    path("article/<int:text_id>/add_highlight/", views.add_highlight, name="add_highlight"),
    path("read/<int:text_id>/", views.read, name="read"),
    path("deleted/<int:text_id>/", views.deleted, name="deleted"),
    path("stats/", views.stats, name='stats'),
    path("highlights/", views.highlights, name='highlights'),
]
