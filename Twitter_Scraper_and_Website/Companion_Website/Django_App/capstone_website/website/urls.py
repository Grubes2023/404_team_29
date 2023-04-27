from django.urls import path
from . import views


urlpatterns = [
    path('',views.index, name='index'), #creating the views for the website, which refrences the index and attaches the url to be just the standard for the notifications tab
    path('about/',views.about, name='about')#creating the view and url extension for the help page
]