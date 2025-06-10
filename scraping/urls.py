from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home_view"),
    path("scrape-hacker-news/", views.scrape_hacker_news, name="scrape_hacker_news"),
]