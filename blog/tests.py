from http.client import responses

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_changed
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment


# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        self.user_obama.is_staff = True
        self.user_obama.save()

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

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_obama,
            content='첫 번째 댓글입니다.'
        )


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
        # setUp()에서 만든 post와 comment를 재사용
        post_001 = self.post_001

        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = soup.find('div', id='post-area')

        self.assertIn(post_001.title, post_area.text)
        self.assertIn(post_001.author.username.upper(), post_area.text)
        self.assertIn(post_001.author.username.upper(), main_area.text)
        self.assertIn(post_001.content, post_area.text)

        # 댓글 영역 검사
        comments_area = soup.find('div', id='comment-area')
        self.assertIsNotNone(comments_area, "댓글 영역(comment-area)이 없습니다.")

        comment_001_area = comments_area.find('div', id=f'comment-{self.comment_001.pk}')
        self.assertIsNotNone(comment_001_area, f"댓글 comment-{self.comment_001.pk}이 없습니다.")

        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

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

    def test_create_post(self):
        #로그인하지 않으면 status code가 200이면 안된다!
        response = self.client.get("/blog/create_post/")
        self.assertNotEqual(response.status_code, 200)

        #스태프가 아닌 trump가 로그인을 한다.
        self.client.login(username="trump", password="somepassword")
        response = self.client.get("/blog/create_post/")
        self.assertNotEqual(response.status_code, 200)

        #스태프인 obama가 로그인을 한다
        self.client.login(username="obama", password="somepassword")
        response = self.client.get("/blog/create_post/")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual("Create Post - Blog", soup.title.text.strip())
        main_area = soup.find('div',id='main-area')
        self.assertIn("Create New Post", main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            "/blog/create_post/",
            {
                "title": "Post Form 만들기",
                "content": "Post Form 페이지를 만듭시다.",
                "tag_str" : "new tag; 한글 태그, python"
            }
        )

        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.content, "Post Form 페이지를 만듭시다.")
        self.assertEqual(last_post.author.username, "obama")

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f"/blog/update_post/{self.post_003.pk}/"

        #로그인 하지 않은 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        #로그인은 했지만, 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(username=self.user_trump.username, password="somepassword")
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        #작성자 본인이 접근하는 경우 (obama)
        self.client.login(
            username=self.user_obama.username, password="somepassword"
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual("Edit Post - Blog", soup.title.text.strip())
        main_area = soup.find('div',id='main-area')
        self.assertIn("Edit Post", main_area.text.strip())

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn("파이썬 공부; python", tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                "title" : "세번쨰 포스트를 수정했습니다.",
                "content" : "안녕 세계? 우리는 하나!",
                "category" : self.category_music.pk,
                "tag_str" : '파이썬 공부; 한글 태그, some tag'
            },
            follow=True,
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div',id='main-area')
        self.assertIn("세번쨰 포스트를 수정했습니다.", main_area.text.strip())
        self.assertIn("안녕 세계? 우리는 하나!", main_area.text.strip())
        self.assertIn(self.category_music.name, main_area.text.strip())
        self.assertIn("파이썬 공부", main_area.text.strip())
        self.assertIn("한글 태그", main_area.text.strip())
        self.assertIn("some tag", main_area.text.strip())

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

        # 🔹 1. 로그인하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertIn("Log in and leave a comment", comment_area.text)
        self.assertIsNone(comment_area.find("form", id="comment-form"))

        # 🔹 2. 로그인 후
        self.client.login(username='obama', password='somepassword')

        response = self.client.get(self.post_001.get_absolute_url())
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn("Log in and leave a comment", comment_area.text)

        comment_form = comment_area.find('form', id='comment-form')
        self.assertIsNotNone(comment_form.find("textarea", id="id_content"))

        from django.urls import reverse
        url = reverse('new_comment', kwargs={'pk': self.post_001.pk})
        response = self.client.post(
            url,
            {
                "content": "오바마의 댓글입니다.",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last()
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn("obama", new_comment_div.text)
        self.assertIn("오바마의 댓글입니다.", new_comment_div.text)

    def test_comment_update(self):
        comment_by_trump = Comment.objects.create(
            post=self.post_001, author=self.user_trump, content="트럼프 댓글입니다."
        )

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')

        # 로그인 전에는 수정 버튼 안 보여야 함
        self.assertIsNone(comment_area.find("a", id=f"comment-{comment_by_trump.pk}-update-btn"))

        # 로그인 후
        self.client.login(username=self.user_trump.username, password="somepassword")
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        comment_update_btn = comment_area.find("a", id=f"comment-{comment_by_trump.pk}-update-btn")
        self.assertIsNotNone(comment_update_btn)
        self.assertIn("edit", comment_update_btn.text)
        self.assertEqual(comment_update_btn.attrs["href"], f"/blog/update_comment/{comment_by_trump.pk}")



