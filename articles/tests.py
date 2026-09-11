from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Article, Category
from .serializers import ArticleSerializer, CategorySerializer


User = get_user_model()


class CategorySerializerTests(TestCase):
    def test_category_name_is_trimmed(self):
        serializer = CategorySerializer(data={'name': '  技术  '})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()

        self.assertEqual(category.name, '技术')

    def test_category_name_is_case_insensitively_unique(self):
        Category.objects.create(name='Technology')
        serializer = CategorySerializer(data={'name': 'technology'})

        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


class CategoryApiTests(APITestCase):
    def test_categories_can_be_listed_without_authentication(self):
        Category.objects.create(name='技术')
        Category.objects.create(name='生活')

        response = self.client.get('/api/categories/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [item['name'] for item in response.data],
            ['技术', '生活'],
        )


class ArticleSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='article_author',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(name='技术')

    def test_article_serializer_accepts_markdown_json(self):
        serializer = ArticleSerializer(data={
            'title': '  Django 入门  ',
            'summary': '文章摘要',
            'content': {
                'format': 'markdown',
                'body': '# 标题\n\n正文',
            },
            'category': self.category.id,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        article = serializer.save(author=self.user)

        self.assertEqual(article.title, 'Django 入门')
        self.assertEqual(article.author, self.user)
        self.assertEqual(article.content['format'], 'markdown')

    def test_article_serializer_rejects_invalid_content_format(self):
        serializer = ArticleSerializer(data={
            'title': '无效文章',
            'summary': '',
            'content': {
                'format': 'html',
                'body': '<p>正文</p>',
            },
            'category': self.category.id,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

    def test_article_serializer_rejects_title_over_thirty_characters(self):
        serializer = ArticleSerializer(data={
            'title': '一' * 31,
            'summary': '',
            'content': {'format': 'markdown', 'body': '正文'},
            'category': self.category.id,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_article_serializer_rejects_summary_over_forty_five_characters(self):
        serializer = ArticleSerializer(data={
            'title': '文章标题',
            'summary': '一' * 46,
            'content': {'format': 'markdown', 'body': '正文'},
            'category': self.category.id,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('summary', serializer.errors)

    def test_article_serializer_keeps_author_read_only(self):
        serializer = ArticleSerializer(data={
            'title': '文章',
            'summary': '',
            'content': {
                'format': 'markdown',
                'body': '正文',
            },
            'category': self.category.id,
            'author': self.user.id,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('author', serializer.validated_data)


class ArticleApiTests(APITestCase):
    list_url = '/api/articles/'

    def setUp(self):
        self.password = 'StrongPass123!'
        self.author = User.objects.create_user(
            username='article_author',
            password=self.password,
        )
        self.other_user = User.objects.create_user(
            username='other_user',
            password=self.password,
        )
        self.tech_category = Category.objects.create(name='技术开发')
        self.life_category = Category.objects.create(name='生活记录')
        self.article = Article.objects.create(
            title='第一篇文章',
            summary='文章摘要',
            content={'format': 'markdown', 'body': '# 正文'},
            author=self.author,
            category=self.tech_category,
        )

    def authenticate(self, user):
        response = self.client.post(
            '/api/auth/login/',
            {'username': user.username, 'password': self.password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def article_payload(self, **overrides):
        payload = {
            'title': '新文章',
            'summary': '新摘要',
            'content': {
                'format': 'markdown',
                'body': '# 新文章正文',
            },
            'category': self.tech_category.id,
        }
        payload.update(overrides)
        return payload

    def test_article_list_is_public_and_paginates_five_articles_per_page(self):
        Article.objects.create(
            title='生活文章',
            summary='',
            content={'format': 'markdown', 'body': '生活'},
            author=self.author,
            category=self.life_category,
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 2)

    def test_article_list_filters_by_category_keyword(self):
        Article.objects.create(
            title='生活文章',
            summary='',
            content={'format': 'markdown', 'body': '生活'},
            author=self.author,
            category=self.life_category,
        )

        response = self.client.get(self.list_url, {'category': '开发'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category'], self.tech_category.id)

    def test_article_response_includes_author_name(self):
        response = self.client.get(f'{self.list_url}{self.article.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['author_name'], self.author.username)
        self.assertIsNone(response.data['updated_at'])

    def test_article_list_can_filter_by_author(self):
        Article.objects.create(
            title='其他作者文章',
            summary='',
            content={'format': 'markdown', 'body': '正文'},
            author=self.other_user,
            category=self.tech_category,
        )

        response = self.client.get(self.list_url, {'author': self.author.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['author'], self.author.id)

    def test_article_list_returns_at_most_ten_articles_per_page(self):
        for index in range(10):
            Article.objects.create(
                title=f'文章 {index}',
                summary='',
                content={'format': 'markdown', 'body': '正文'},
                author=self.author,
                category=self.tech_category,
            )

        first_page = self.client.get(self.list_url, {'page': 1})
        second_page = self.client.get(self.list_url, {'page': 2})

        self.assertEqual(first_page.status_code, status.HTTP_200_OK)
        self.assertEqual(first_page.data['count'], 11)
        self.assertEqual(len(first_page.data['results']), 10)
        self.assertEqual(len(second_page.data['results']), 1)

    def test_normal_user_can_create_category(self):
        self.authenticate(self.other_user)

        response = self.client.post(
            '/api/categories/',
            {'name': '新分类'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '新分类')

    def test_article_list_filters_by_title_keyword(self):
        Article.objects.create(
            title='Django REST 实践',
            summary='',
            content={'format': 'markdown', 'body': '正文'},
            author=self.author,
            category=self.tech_category,
        )
        Article.objects.create(
            title='Vue 前端实践',
            summary='',
            content={'format': 'markdown', 'body': '正文'},
            author=self.author,
            category=self.tech_category,
        )

        response = self.client.get(self.list_url, {'title': 'django'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Django REST 实践')

    def test_authenticated_user_can_create_article(self):
        self.authenticate(self.other_user)

        response = self.client.post(
            self.list_url,
            self.article_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Article.objects.get(pk=response.data['id'])
        self.assertEqual(created.author, self.other_user)

    def test_anonymous_user_cannot_create_article(self):
        response = self.client.post(
            self.list_url,
            self.article_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_can_update_own_article(self):
        self.authenticate(self.author)

        response = self.client.patch(
            f'{self.list_url}{self.article.id}/',
            {'title': '修改后的标题'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, '修改后的标题')
        self.assertIsNotNone(self.article.updated_at)

    def test_other_user_cannot_update_or_delete_article(self):
        self.authenticate(self.other_user)

        update_response = self.client.patch(
            f'{self.list_url}{self.article.id}/',
            {'title': '越权修改'},
            format='json',
        )
        delete_response = self.client.delete(
            f'{self.list_url}{self.article.id}/',
        )

        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Article.objects.filter(pk=self.article.id).exists())

    def test_author_can_delete_own_article(self):
        self.authenticate(self.author)

        response = self.client.delete(f'{self.list_url}{self.article.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.article.refresh_from_db()
        self.assertTrue(self.article.is_deleted)
        detail_response = self.client.get(f'{self.list_url}{self.article.id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)
