import posts
from django.views.generic import ListView, DetailView
from .models import Post

class PostList(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'blog/post_list.html'


class PostDetail(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'