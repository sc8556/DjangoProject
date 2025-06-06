from django.urls import path
from . import  views
from .views import PostDetail

urlpatterns = [
    path('/<int:pk>/', PostDetail.as_view()),
    path('', views.PostList.as_view()),
    # path('/<int:pk>/', views.single_post_page), #CBV 작업에 따라 주석처리
    # path('', views.index), #CBV 작업에 따라 주석처리
]