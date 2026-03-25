from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # OTP related URLs
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('register-with-otp/', views.register_with_otp_view, name='register_with_otp'),

    # Password management
    path('change-password/', views.change_password_view, name='change_password'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('password-reset-confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
]