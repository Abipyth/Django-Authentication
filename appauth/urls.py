from django.urls import path
from appauth import views
urlpatterns = [
    path('signup', views.signup, name='signup'),
    
    
]
