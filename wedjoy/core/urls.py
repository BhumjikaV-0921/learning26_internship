from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
     path('',views.home, name='home'),
    path('signup/',views.userSignupView,name='signup'),
    path('login/',views.userLoginView,name='login'),
    path("logout/", views.custom_logout, name="logout"),
   path('aboutus/', views.aboutus, name='aboutus'),
   path('profile/', views.Userprofile, name='Userprofile'),

    path('userregisteredevents/',views.userregisteredevents, name='userregisteredevents'),
    path('uservolunteering/',views.uservolunteering, name='uservolunteering'),
    path('usercomments/',views.usercomments, name='usercomments'),
    path('usersecurity/',views.usersecurity, name='usersecurity'),
    path('userupdateprofile/',views.userupdateprofile, name='userupdateprofile'),
    path('professional-networking/', views.professional_networking, name='professional_networking'),
    path('job-listings/', views.job_listings, name='job_listings'),
    path('consulting/', views.consulting, name='consulting'),
    path('premium-membership/', views.premium_membership, name='premium_membership'),
    path('careers/', views.careers, name='careers'),
]
