from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()


class PostFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )

    def test_can_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_can_edit_post(self):
        old_text = self.post.text
        form_data = {
            'text': 'Текст изменён',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(old_text, form_data['text'],
                            'Пользователь не может изменить пост')
        self.assertEqual(response.status_code, 200)
