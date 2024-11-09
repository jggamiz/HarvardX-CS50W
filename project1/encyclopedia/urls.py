from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry_page, name="entry_page"),
    path("search/", views.search, name="search"),
    path("newpage/", views.newpage, name="newpage"),
    path("wiki/<str:title>/edit", views.edit, name="editpage"),
    path("random/", views.randompage, name="randompage")
]
