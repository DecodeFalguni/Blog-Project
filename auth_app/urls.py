from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view,name='register'),
    path('login/', views.login_view,name='login'),
    path('', views.dashboard_view,name='dashboard'),
    path('logout/', views.logout_view,name='logout'),
    path('profile/', views.user_profile_view,name='profile'),
    path('verify_otp/<int:user_id>/', views.verify_otp_view, name='verify_otp'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]