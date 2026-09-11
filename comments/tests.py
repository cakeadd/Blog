from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article, Category

from .models import Comment


User = get_user_model()


class CommentModelTests(TestCase):
    def test_comment_belongs_to_article_and_author_without_updated_at(self):
        user = User.objects.create_user(
            username='comment_user',
            password='StrongPass123!',
        )
        category = Category.objects.create(name='评论测试')
        article = Article.objects.create(
            title='评论测试文章',
            content={'format': 'markdown', 'body': '正文'},
            author=user,
            category=category,
        )

        comment = Comment.objects.create(
            article=article,
            author=user,
            content='这是一条评论。',
        )

        self.assertEqual(comment.article, article)
        self.assertEqual(comment.author, user)
        self.assertEqual(comment.content, '这是一条评论。')
        self.assertIsNotNone(comment.created_at)
        self.assertFalse(hasattr(comment, 'updated_at'))


class CommentApiTests(APITestCase):
    def setUp(self):
        self.password = 'StrongPass123!'
        self.author = User.objects.create_user(
            username='comment_author',
            password=self.password,
        )
        self.other_user = User.objects.create_user(
            username='comment_other',
            password=self.password,
        )
        category = Category.objects.create(name='评论接口测试')
        self.article = Article.objects.create(
            title='评论接口文章',
            content={'format': 'markdown', 'body': '正文'},
            author=self.author,
            category=category,
        )
        self.comment = Comment.objects.create(
            article=self.article,
            author=self.author,
            content='已有评论',
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

    def test_comments_can_be_listed_publicly(self):
        response = self.client.get(
            f'/api/articles/{self.article.id}/comments/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], '已有评论')
        self.assertEqual(response.data[0]['author_name'], self.author.username)

    def test_authenticated_user_can_create_comment(self):
        self.authenticate(self.other_user)

        response = self.client.post(
            f'/api/articles/{self.article.id}/comments/',
            {'content': '新评论'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(pk=response.data['id'])
        self.assertEqual(comment.article, self.article)
        self.assertEqual(comment.author, self.other_user)

    def test_anonymous_user_cannot_create_comment(self):
        response = self.client.post(
            f'/api/articles/{self.article.id}/comments/',
            {'content': '匿名评论'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_author_can_delete_own_comment(self):
        self.authenticate(self.author)

        response = self.client.delete(f'/api/comments/{self.comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)
        list_response = self.client.get(
            f'/api/articles/{self.article.id}/comments/'
        )
        self.assertEqual(list_response.data, [])

    def test_user_cannot_delete_another_users_comment(self):
        self.authenticate(self.other_user)

        response = self.client.delete(f'/api/comments/{self.comment.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(pk=self.comment.id).exists())

    def test_comment_cannot_be_updated(self):
        self.authenticate(self.author)

        response = self.client.patch(
            f'/api/comments/{self.comment.id}/',
            {'content': '修改评论'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
