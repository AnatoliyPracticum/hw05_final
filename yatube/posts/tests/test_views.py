from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, Follow, User
from posts.forms import PostForm
from django.conf import settings


class PostsPagesTests(TestCase):
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
            text='Тестовый пост длиннее пятнадцати символов',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostsPagesTests.user)

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """- Проверка соответствия URLname - шаблон"""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user}): 'posts/profile.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.pk}): 'posts/create_post.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:index'): 'posts/index.html'}
        # Проверяем, что при обращении к name вызывается соответствующий
        # HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_page_show_correct_context(self):
        """- Проверка контекста страницы post_index"""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        self.check_context_contains_page_or_post(response.context)

    def test_group_posts_page_show_correct_context(self):
        """- Проверка контекста страницы group_posts"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group.slug}))
        self.assertEqual(response.context['group'], self.group)
        self.check_context_contains_page_or_post(response.context)

    def test_profile_page_show_correct_context(self):
        """- Проверка контекста страницы profile"""
        # self.post = PostsPagesTests.post
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': self.user}))
        self.assertEqual(response.context['username'], self.user)
        self.check_context_contains_page_or_post(response.context)

    def test_post_detail_page_show_correct_context(self):
        """- Проверка контекста страницы post_detail"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': self.post.pk}))
        self.check_context_contains_page_or_post(response.context, post=True)

    def test_create_post_page_show_correct_context(self):
        """- Проверка контекста страницы create_post"""
        pages = ((reverse('posts:post_create'), False), (reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}), True), )
        for url, is_edit_value in pages:
            response = self.authorized_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], PostForm)

            self.assertIn('is_edit', response.context)
            is_edit = response.context['is_edit']
            self.assertIsInstance(is_edit, bool)
            self.assertEqual(is_edit, is_edit_value)

    def test_paginator_contains_count(self):
        """- Проверка пагинатора для всех страниц"""
        # Добавляем несколько постов,
        # чтобы количество постов в тестовой базе превышало количество на
        # странице
        count_posts_paginator_tests = 13
        paginator_objects = []
        for i in range(0, count_posts_paginator_tests):
            new_post = Post(
                author=self.user,
                text='Тестовый пост ' + str(i),
                group=self.group
            )
            paginator_objects.append(new_post)
        Post.objects.bulk_create(paginator_objects)
        # Формируем словарь адресов и
        # словарь соответствия сколько ожидается постов на каждой странице
        url_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile',
                args=[self.user]
            )]
        page_limit_second = len(
            Post.objects.all()) - settings.POSTS_PER_PAGE
        pages = (
            (1, settings.POSTS_PER_PAGE),
            (2, page_limit_second)
        )
        for url in url_names:
            for page, expected_count in pages:
                response = self.authorized_client.get(url, {"page": page})
                self.assertEqual(
                    len(response.context['page_obj']), expected_count)

    def test_post_group_index_exists(self):
        """- Проверка наличия поста с указанной группой на Главной странице"""
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertIn(self.post, response.context['page_obj'])

    def test_post_right_group_exists(self):
        """- Проверка наличия поста с указанной группой на странице Группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.post.group.slug})
        )
        self.assertIn(self.post, response.context['page_obj'])

    def test_post_false_group_not_exists(self):
        """- Проверка отсутствия поста с группой на странице другой Группы"""
        another_group = Group.objects.create(
            title='другая Тестовая группа',
            slug='slug_another_test_group',
            description='Тестовое описание группы'
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': another_group.slug})
        )
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_post_group_exists_at_author(self):
        """- Проверка наличия поста с указанной группой на странице Автора"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author})
        )
        self.assertIn(self.post, response.context['page_obj'])

    def test_index_page_cache(self):
        """- Проверка кэширования главной страницы"""
        post = Post.objects.create(
            author=self.user,
            text='Пост для проверки кэша',
            group=self.group
        )
        response_1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.get(pk=post.id).delete()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_3.content)

    def test_follow(self):
        """- Проверка добавления подписки"""
        author = User.objects.create_user(username='AuthorNoName')
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': author})
        )
        following = Follow.objects.get(user=self.user)
        self.assertEqual(author, following.author)

    def test_unfollow(self):
        """- Проверка отключения подписки"""
        author = User.objects.create_user(username='AuthorNoName')
        Follow.objects.create(user=self.user, author=author)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': author})
        )
        with self.assertRaises(Follow.DoesNotExist):
            Follow.objects.get(user=self.user, author=author)

    def test_follow_contain_post_for_follower(self):
        """- Проверка наличия поста избранного автора в ленте follow"""
        author = User.objects.create_user(username='AuthorNoName')
        Follow.objects.create(user=self.user, author=author)
        followed_post = Post.objects.create(
            text='Тестовый пост длиннее пятнадцати символов',
            author=author,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(followed_post, response.context['page_obj'])

    def test_follow_contain_post_for_follower(self):
        """- Проверка отсутствия поста избранного автора в ленте follow"""
        author = User.objects.create_user(username='AuthorNoName')
        post = Post.objects.create(
            text='Тестовый пост длиннее пятнадцати символов',
            author=author,
        )
        # Проверка, что подписки нет
        with self.assertRaises(Follow.DoesNotExist):
            Follow.objects.get(user=self.user, author=author)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'])
