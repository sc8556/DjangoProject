from django.urls import path
from . import  views
from .views import PostDetail

urlpatterns = [
    path('delete_comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view(), name='comment_update'),
    path('update_post/<int:pk>/',views.PostUpdate.as_view(), name='post_update'),
    path('create_post/',views.PostCreate.as_view(), name='post_create'),
    path('tag/<str:slug>/', views.tag_page,name='tag_page'),
    path('category/<str:slug>/', views.category_page,name='category_page'),
    path('<int:pk>/new_comment/', views.new_comment, name='new_comment'),
    path('', views.PostList.as_view(),name='post_list'),
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
]