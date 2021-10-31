from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        Group.objects.create(
            title='Тестовая группа',
            slug='test_group'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_group/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexisting_url(self):
        response = self.authorized_client.get('/testtest')
        self.assertEquals(
            response.status_code, 404,
            'unexisting_url не работает')

    def test_rights_edit(self):
        response = self.guest_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/posts/1/')
        response_author = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response_author.status_code, 200,
                         'автор не может редактировать свой пост')

    def test_rights_create(self):
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')
        response_auth = self.authorized_client.get('/create/')
        self.assertEqual(response_auth.status_code, 200,
                         'активный пользователь не может создать пост')
