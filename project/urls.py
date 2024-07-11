
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('',include('app1.urls')),
    path("appauth/",include("appauth.urls"))
]
