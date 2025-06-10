from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home_view"),
    path('author/<str:name>/', views.AuthorDetailView.as_view(), name='author_detail'),
]