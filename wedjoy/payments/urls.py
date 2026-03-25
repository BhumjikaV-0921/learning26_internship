from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create-order/<int:event_id>/', views.create_payment_order, name='create_payment_order'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('history/', views.payment_history, name='payment_history'),
]