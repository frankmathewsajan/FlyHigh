from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mapped', views.disease, name='disease'),
    path('enclosed', views.enclosed, name='enclosed'),

]
