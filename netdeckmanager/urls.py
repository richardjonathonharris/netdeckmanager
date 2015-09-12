from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/', views.search_for_deck, name='search_for_deck'),
]
