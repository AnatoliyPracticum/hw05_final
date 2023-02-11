from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длиннее пятнадцати симоволов',
            group=cls.group
        )

    def subtest_list_assertequal(self, expected_list):
        for field, expected_field in expected_list.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_field)

    def test_models_have_correct_object_names(self):
        """- Проверка __str__ моделей"""
        fields_str_model = {
            str(self.post): self.post.text[:15],
            str(self.group): self.group.title}
        PostModelTest.subtest_list_assertequal(self, fields_str_model)

    def test_post_help_text(self):
        """- Проверка help_text модель Post"""
        expected_post_help_texts = {
            self.post._meta.get_field('text').help_text: 'Введите текст поста',
            self.post._meta.get_field('group').help_text:
                'Группа, к которой будет относиться пост',
        }
        PostModelTest.subtest_list_assertequal(self, expected_post_help_texts)

    def test_post_verbose_name(self):
        """- Проверка verbose_name модель Post"""
        expected_post_verbose_names = {
            self.post._meta.get_field(
                'text').verbose_name: 'Текст поста',
            self.post._meta.get_field(
                'pub_date').verbose_name: 'Дата создания',
            self.post._meta.get_field(
                'author').verbose_name: 'Автор',
            self.post._meta.get_field(
                'group').verbose_name: 'Группа',
        }
        PostModelTest.subtest_list_assertequal(
            self, expected_post_verbose_names)

    def test_group_verbose_name(self):
        """- Проверка verbose_name модель Group"""
        expected_group_verbose_names = {
            self.group._meta.get_field(
                'title').verbose_name: 'Название группы',
            self.group._meta.get_field(
                'slug').verbose_name: 'Группа',
            self.group._meta.get_field(
                'description').verbose_name: 'Описание группы'
        }
        PostModelTest.subtest_list_assertequal(
            self, expected_group_verbose_names)
