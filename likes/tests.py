from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article, Category

from .models import Like


User = get_user_model()


class LikeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='like_user',
            password='StrongPass123!',
        )
        category = Category.objects.create(name='点赞测试')
        self.article = Article.objects.create(
            title='点赞测试文章',
            content={'format': 'markdown', 'body': '正文'},
            author=self.user,
            category=category,
        )

    def test_user_can_like_an_article_once(self):
        like = Like.objects.create(article=self.article, user=self.user)

        self.assertEqual(like.article, self.article)
        self.assertEqual(like.user, self.user)
        self.assertEqual(Like.objects.count(), 1)

    def test_same_user_cannot_like_same_article_twice(self):
        Like.objects.create(article=self.article, user=self.user)

        with self.assertRaises(IntegrityError):
            Like.objects.create(article=self.article, user=self.user)


class ArticleLikeApiTests(APITestCase):
    def setUp(self):
        self.password = 'StrongPass123!'
        self.user = User.objects.create_user(
            username='like_api_user',
            password=self.password,
        )
        category = Category.objects.create(name='点赞接口测试')
        self.article = Article.objects.create(
            title='点赞接口文章',
            content={'format': 'markdown', 'body': '正文'},
            author=self.user,
            category=category,
        )
        self.url = f'/api/articles/{self.article.id}/like/'

    def authenticate(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': self.user.username, 'password': self.password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_like_requires_authentication(self):
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_can_query_like_count_but_cannot_like(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 0)

        post_response = self.client.post(self.url, {}, format='json')
        self.assertEqual(post_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_like_article(self):
        self.authenticate()

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 1)
        self.assertEqual(Like.objects.count(), 1)

    def test_repeated_like_is_idempotent(self):
        self.authenticate()
        first_response = self.client.post(self.url, {}, format='json')
        second_response = self.client.post(self.url, {}, format='json')

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertTrue(second_response.data['liked'])
        self.assertEqual(second_response.data['likes_count'], 1)
        self.assertEqual(Like.objects.count(), 1)

    def test_user_can_query_like_status(self):
        self.authenticate()

        not_liked_response = self.client.get(self.url)
        Like.objects.create(article=self.article, user=self.user)
        liked_response = self.client.get(self.url)

        self.assertEqual(not_liked_response.status_code, status.HTTP_200_OK)
        self.assertFalse(not_liked_response.data['liked'])
        self.assertEqual(not_liked_response.data['likes_count'], 0)
        self.assertTrue(liked_response.data['liked'])
        self.assertEqual(liked_response.data['likes_count'], 1)

    def test_user_can_cancel_like(self):
        self.authenticate()
        Like.objects.create(article=self.article, user=self.user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 0)
        self.assertFalse(Like.objects.exists())

    def test_cancel_like_is_idempotent(self):
        self.authenticate()

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 0)

    def test_user_can_list_liked_articles(self):
        self.authenticate()
        Like.objects.create(article=self.article, user=self.user)

        response = self.client.get('/api/likes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.article.id)

    def test_liked_article_list_hides_deleted_articles(self):
        self.authenticate()
        Like.objects.create(article=self.article, user=self.user)
        self.article.is_deleted = True
        self.article.save(update_fields=['is_deleted'])

        response = self.client.get('/api/likes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
