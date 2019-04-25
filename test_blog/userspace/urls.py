from django.urls import path

from .views import HomeView, NewsBarView

urlpatterns = [
    path('news_bar', NewsBarView.as_view(), name="news-bar"),
    path('', HomeView.as_view(), name="home"),
]

