from django.db import models
from django.contrib.auth.models import User
from markdown import markdown
from markdownx.models import MarkdownxField
import os

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook = models.CharField(max_length=100, blank=True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/',blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/',blank=True)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User,on_delete=models.SET_NULL, null=True)

    category = models.ForeignKey('Category',on_delete=models.SET_NULL, null=True, blank=True)

    tags = models.ManyToManyField('Tag',blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}'

    def get_absolute_url(self):
        return f"/blog/{self.pk}/"

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_extension(self):
        return os.path.splitext(self.file_upload.name)[-1]

    def get_content_markdown(self):
        return markdown(self.content)

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"

    class Meta:
        verbose_name_plural = 'Categories'

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/tag/{self.slug}/"

class Comment(models.Model):
    post = models.ForeignKey('Post',on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[{self.author}]::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'