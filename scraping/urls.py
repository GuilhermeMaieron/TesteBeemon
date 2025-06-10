from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home_view"),
    path("scrape_quotes/", views.scrape_quotes, name="scrape_quotes"),
]