import posts
# from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post

class PostList(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'blog/index.html'
# def index(request):
#     posts = Post.objects.all().order_by('-pk') # 모든 post를 가져옴
#
#     return render(
#                 request,
#     'blog/post_list.html',
#         {
#                 'posts' : posts,
#                 }
#                 )

class PostDetail(DetailView):
    model = Post

# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/single_post_page.html',
#         {
#             'post' : post,
#         }
#     )