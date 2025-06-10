from django.urls import path
from . import  views
from .views import PostDetail

urlpatterns = [
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/', PostDetail.as_view()),
    path('', views.PostList.as_view()),
]