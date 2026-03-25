from django.urls import path
from . import views

urlpatterns = [
    # Example route
    # path('', views.business_home, name='business_home'),
    path('showvolunteers/', views.showvounteers, name='showvolunteers'),
    path('register/<int:event_id>/', views.volunteer_register, name='volunteer_register'),

]