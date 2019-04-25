from django.urls import path

from .views import HomeView, NewsBarView, Subscribe, BlogsList

urlpatterns = [
    path('news_bar/', NewsBarView.as_view(), name="news-bar"),
    path('blogs_list/', BlogsList.as_view(), name="blogs-list"),
    path('subscribe/', Subscribe.as_view(), name="subscribe"),
    path('', HomeView.as_view(), name="home"),
]

