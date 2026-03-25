# adminpanel/urls.py
from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
        # ===  urls user =====
    path('users/', views.manage_users, name='users'),
    path("admin/users/suspend/<int:id>/", views.suspend_user, name="suspend_user"),
    path("admin/users/activate/<int:id>/", views.activate_user, name="activate_user"),
    path("admin/users/delete/<int:id>/", views.delete_user, name="delete_user"),

    # ==== events urls =====

    path('events/', views.manage_events, name='events'),
    path('events/approve/<int:id>/', views.approve_event, name='approve_event'),
    path('events/reject/<int:id>/', views.reject_event, name='reject_event'),
    path('events/delete/<int:id>/', views.delete_event, name='delete_event'),

    # ==== businness urls ======
    path('businesses/', views.manage_businesses, name='businesses'),
    path('business/approve/<int:id>/', views.approve_business, name='approve_business'),
    path('business/reject/<int:id>/', views.reject_business, name='reject_business'),
    path('business/delete/<int:id>/', views.delete_business, name='delete_business'),

    # ======= volunteers ========
    path('volunteers/', views.volunteer_list, name='volunteer_list'),
    path('volunteers/create/', views.create_volunteer, name='create_volunteer'),
    path('volunteers/edit/<int:id>/', views.edit_volunteer, name='edit_volunteer'),
    path('volunteers/delete/<int:id>/', views.delete_volunteer, name='delete_volunteer'),
    path('volunteers/<int:id>/', views.volunteer_participants, name='participants'),
    path('participants/complete/<int:id>/', views.mark_completed, name='mark_completed'),       
]