from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    # Список постов по группам
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # Подписки
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    # Добавление комментария к посту
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'),
    # Редактирование записи
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Просмотр записи
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Создание записи
    path('create/', views.post_create, name='post_create'),
    path('follow/', views.follow_index, name='follow_index'),
]
