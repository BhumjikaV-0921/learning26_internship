from django.urls import path
from . import views

urlpatterns = [
    # Example route
    # path('', views.business_home, name='business_home'),
    path('showEvents/', views.showEvents, name='showEvents'),
    path('eventDetail/<int:event_id>', views.events, name='events'),
    path('event/<int:event_id>/rsvp/', views.Eventrsvp, name='Eventrsvp'),
]