from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # main page
    path('', views.index, name='index'),
    # page for a certain group
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # User profile
    path('profile/<str:username>/', views.profile, name='profile'),
    # One post view
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Create a new post
    path('create/', views.post_create, name='post_create'),
    # Edit post page
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Comment path
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'),
    # Follow path
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name="profile_unfollow"
    ),
]
