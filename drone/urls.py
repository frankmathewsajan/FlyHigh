
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('mapper', views.map_view, name='map'),
]
