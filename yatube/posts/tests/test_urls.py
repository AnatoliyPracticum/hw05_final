# posts/tests/test_urls.py
from django.test import TestCase, Client
from posts.models import Post, Group, User
from http import HTTPStatus


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_test_group',
            description='Тестовое описание группы'

        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=Group.objects.get(title='Тестовая группа')
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostsURLTests.user)

    def test_url_exists_at_desired_location_guest(self):
        """- Проверка доступа страниц гостем"""
        # Шаблоны по адресам
        list_url_code_guest = {
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.FOUND,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            '/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/comment': HTTPStatus.MOVED_PERMANENTLY
        }
        for address, expected_status in list_url_code_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    expected_status,
                    f'Открытие "{address}" гостем')

    def test_url_exists_at_desired_location_authorized(self):
        """- Проверка доступа страниц авторизованным пользователем"""
        # Шаблоны по адресам
        list_url_code_guest = {
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostsURLTests.user}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/': HTTPStatus.OK,
            '/unexistingPage/': HTTPStatus.NOT_FOUND,
            f'/posts/{self.post.pk}/comment': HTTPStatus.MOVED_PERMANENTLY
        }
        for address, expected_status in list_url_code_guest.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    expected_status,
                    f'Открытие "{address}" авторизованным пользователем')

    def test_url_redirect_at_correct_location(self):
        """- Проверка редиректа неавторизованного пользователя"""
        # Шаблоны по адресам
        list_url_code_guest = {
            f'/posts/{self.post.pk}/edit/': ('/auth/login/?next='
                                             f'/posts/{self.post.pk}/edit/'),
            '/create/': '/auth/login/?next=/create/',
        }
        for address, expected_status in list_url_code_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response,
                                     expected_status)

    def test_urls_uses_correct_template(self):
        """- Проверка соответствия URL-адрес - шаблон"""
        # Шаблоны по адресам
        templates_url_names = {
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostsURLTests.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/': 'posts/index.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
