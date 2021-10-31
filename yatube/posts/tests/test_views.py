from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group
from django import forms

User = get_user_model()


class PostPagesTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group'
        )
        for i in range(1, 13):
            Post.objects.create(
                text='Тестовый текст',
                author=self.user,
                group=self.group
            )

    def test_views_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_group'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}): 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text

        response2 = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), 10, 'первая страница index')
        self.assertEqual(len(
            response2.context['page_obj']), 3, 'вторая страница index')

        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_group'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group

        response2 = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': 'test_group'}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), 10, 'первая страница group_posts')
        self.assertEqual(len(
            response2.context['page_obj']), 2, 'вторая страница group_posts')

        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_user_0 = first_object.author

        response2 = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}) + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']), 10, 'первая страница profile')
        self.assertEqual(len(
            response2.context['page_obj']), 3, 'вторая страница profile')

        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_user_0, self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}))
        first_object = response.context['post']
        post_text_0 = first_object.text

        self.assertEqual(post_text_0, 'Тестовый текст')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group
        )

        response_index = self.authorized_client.get(reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test_group'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'StasBasov'}))

        objects_index = response_index.context['page_obj']
        objects_group = response_group.context['page_obj']
        objects_profile = response_profile.context['page_obj']

        obj_i_in = False
        obj_g_in = False
        obj_p_in = False

        for object_i in objects_index:
            if (object_i == post):
                obj_i_in = True
        self.assertEquals(obj_i_in, True, 'пост не появился на главной')
        for object_g in objects_group:
            if (object_g == post):
                obj_g_in = True
        self.assertEquals(obj_g_in, True, 'пост не появился в группе')
        for object_p in objects_profile:
            if (object_p == post):
                obj_p_in = True
        self.assertEquals(obj_p_in, True, 'пост не появился в профиле')
