from django.urls import path
from app1 import views
from django.contrib import admin
admin.site.site_header="HOMESTAY ADMIN"
admin.site.site_header="ADMIN"

urlpatterns = [
    path('', views.index, name='index'),
    path("signup",views.signup,name="signup"),
    path("in",views.log,name="in"),
    path("lout",views.lout,name="lout"),
    path("activate/<uidb64>/<token>",views.AccountActivateView.as_view(), name="activate"),
    path("reqresetpw", views.ReqResetPWView.as_view(), name="reqresetpw"),
    path("reset/<uidb64>/<token>",views.ResetNewPWView.as_view(), name="reset")
]
