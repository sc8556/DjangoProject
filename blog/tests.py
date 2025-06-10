from http.client import responses

from django.contrib.auth.models import User
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag


# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬 공부..')
        self.tag_python = Tag.objects.create(name='python', slug='python..')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello..')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world.',
            category=self.category_programming,
            author
            =self.user_trump
        )
        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            category=self.category_music,
            author=self.user_obama
        )

        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='Category가 없어요!!',
            author=self.user_obama
        )

        self.post_001.tags.add(self.tag_hello)
        self.post_001.tags.add(self.tag_python_kor)
        self.post_001.tags.add(self.tag_python)

        self.post_002.tags.add(self.tag_hello)
        self.post_002.tags.add(self.tag_python_kor)
        self.post_002.tags.add(self.tag_python)

        self.post_003.tags.add(self.tag_hello)
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)


    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'],'/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'],'/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'],'/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'],'/about_me/')

    def test_post_list(self):
        #Post가 있는 경우
        self.assertEqual(Post.objects.all().count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn("아직 게시물이 없습니다", main_area.text)

        post_001_card = soup.find('div', id=f'post-{self.post_001.pk}')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertIn(self.tag_python.name, post_001_card.text)
        self.assertIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = soup.find('div', id=f'post-{self.post_002.pk}')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertIn(self.tag_hello.name, post_002_card.text)
        self.assertIn(self.tag_python.name, post_002_card.text)
        self.assertIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = soup.find('div', id=f'post-{self.post_003.pk}')
        self.assertIsNotNone(post_003_card)  # 방어코드

        if self.post_003.category:
            self.assertIn(self.post_003.category.name, post_003_card.text)
        else:
            self.assertIn("미분류", post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)
        self.assertIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        # Post가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        #id가 main-area인 div태그를 찾습니다.
        main_area = soup.find('div', id='main-area')
        self.assertIn("아직 게시물이 없습니다", main_area.text)

    def test_post_detail(self):
        # 1.1 포스트가 하나 있다.
        post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = 'Hello World. We are the world.',
            author = self.user_trump,
            category=self.category_programming,
        )

        # 1.2 그 포스트의 url은 'blog/1'이다
        self.assertEqual(post_001.get_absolute_url(), f'/blog/{post_001.pk}/')

        # 1. 첫 번째 포스트의 상세 페이지 테스트
        # 1.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다.
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1.2 post-list 페이지와 똑같은 네비게이션 바가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 1.3 첫 번째 포스트 제목이 웹 브라우저 탭 타이틀에 들어있다
        self.assertIn(post_001.title, soup.title.text)

        # 1.4 첫 번째 포스트의 제목[title]이 포스트 영역[post-area]에 있다
        main_area = soup.find('div',id='main-area')
        post_area = soup.find('div',id='post-area')
        self.assertIn(post_001.title, post_area.text)
        self.assertIn(self.user_trump.username.upper(), post_area.text)

        # 1.5 첫 번째 post의 작성자[author]가 포스트 영역[post-area]에 있다.
        self.assertIn(post_001.author.username.upper(), main_area.text)

        # 1.6 첫 번째 post의 내용[content]이 포스트 영역[popst-area] 에 있다.
        self.assertIn(post_001.content, post_area.text)

    def category_card_test(self,soup):
            categories_card = soup.find('div',id='categories-card')
            self.assertIn("Categories", categories_card.text)
            self.assertIn(
                f'{self.category_programming.name} ({self.category_programming.post_set.count()})',
                categories_card.text,
            )
            self.assertIn(
                f'{self.category_music.name} ({self.category_music.post_set.count()})',
                categories_card.text,
            )
            self.assertIn(f'미분류 (1)', categories_card.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div',id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div',id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)