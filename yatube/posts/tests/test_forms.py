import shutil
import tempfile

from posts.forms import PostForm
from posts.models import Post, Group, Comment, User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
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
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """- Проверка формы создания поста"""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        input_textfield_form_create = 'Тестовый текст, созданный через форму'
        small_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_image,
            content_type='image/gif'
        )
        form_data = {
            'text': input_textfield_form_create,
            'group': self.group.pk,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={
                    'username': self.user}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным текстом
        self.assertTrue(
            Post.objects.filter(
                text=input_textfield_form_create,
                group=self.group.pk,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """- Проверка формы редактирования поста"""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        input_textfield_testform_edit = 'Измененный текст поста'
        form_data = {
            'text': input_textfield_testform_edit,
            'group': self.group.pk
        }
        response_edit_post = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.pk}),
            form_data,
            follow=True)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response_edit_post, reverse(
                'posts:post_detail', kwargs={
                    'post_id': self.post.pk}))
        # Проверяем, не изменилось ли количество постов
        self.assertEqual(Post.objects.count(), posts_count)

        # Проверяем, что изменилась запись на заданный текст
        self.assertEqual(
            Post.objects.get(pk=self.post.pk).text,
            input_textfield_testform_edit
        )

    def test_comment_post(self):
        """- Проверка формы добавления комментария к посту"""
        # Подсчитаем количество комментариев в Post
        comments_count = Comment.objects.filter(post=self.post.pk).count()
        input_comment_text = 'Текст тестового комментария'
        form_data = {
            'text': input_comment_text,
        }
        response_add_comment = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.pk}),
            form_data,
            follow=True)
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response_add_comment, reverse(
                'posts:post_detail', kwargs={
                    'post_id': self.post.pk}))
        # Проверяем, изменилось ли количество комментариев
        self.assertEqual(
            Comment.objects.filter(
                post=self.post.pk).count(),
            comments_count + 1)

        # Проверяем, что комментарий добавился к посту
        comment = Comment.objects.get(text=input_comment_text)
        self.assertIsNotNone(comment)
        self.assertEqual(
            comment.post,
            self.post)

    def test_comment_post_by_guest(self):
        """- Проверка недоступности для гостя
        формы добавления комментария к посту"""
        # Подсчитаем количество комментариев в Post
        comments_count = Comment.objects.filter(post=self.post.pk).count()
        self.guest_client = Client()
        input_comment_text = 'Текст тестового комментария'
        form_data = {
            'text': input_comment_text,
        }
        self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.pk}),
            form_data,
            follow=True)
        # Проверяем, изменилось ли количество комментариев
        self.assertEqual(
            Comment.objects.filter(
                post=self.post.pk).count(),
            comments_count)

        # Проверяем, что комментарий не добавился к посту
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(text=input_comment_text)
