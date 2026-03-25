from django.urls import path
from . import views

urlpatterns = [
    # Example route
    # path('', views.business_home, name='business_home'),
    path('showbusiness/', views.showbusiness, name='showbusiness'),
    path('business/<int:business_id>/', views.business, name='business'),
]