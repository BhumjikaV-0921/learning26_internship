from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_feed, name='feed'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('my-posts/', views.user_posts, name='user_posts'),
]