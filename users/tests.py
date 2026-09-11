from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image

from articles.models import Article, Category
from likes.models import Like


User = get_user_model()


class UserApiTests(APITestCase):
    register_url = '/api/auth/register/'
    login_url = '/api/auth/login/'
    refresh_url = '/api/auth/token/refresh/'
    me_url = '/api/auth/me/'
    password_url = '/api/auth/password/'

    password = 'StrongPass123!'

    def create_user(self, username='test_user', email='test@example.com'):
        return User.objects.create_user(
            username=username,
            email=email,
            password=self.password,
        )

    def authenticate(self, username='test_user'):
        response = self.client.post(
            self.login_url,
            {'username': username, 'password': self.password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )
        return response.data

    def test_register_creates_normal_user(self):
        response = self.client.post(
            self.register_url,
            {
                'username': 'new_user',
                'email': 'new@example.com',
                'password': self.password,
                'password_confirm': self.password,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='new_user')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.role, User.Role.USER)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password(self.password))
        self.assertNotIn('password', response.data)

    def test_register_rejects_duplicate_username_case_insensitively(self):
        self.create_user(username='ExistingUser')

        response = self.client.post(
            self.register_url,
            {
                'username': 'existinguser',
                'email': 'another@example.com',
                'password': self.password,
                'password_confirm': self.password,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_rejects_different_password_confirmation(self):
        response = self.client.post(
            self.register_url,
            {
                'username': 'new_user',
                'email': 'new@example.com',
                'password': self.password,
                'password_confirm': 'DifferentPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_login_returns_access_and_refresh_tokens(self):
        self.create_user()

        response = self.client.post(
            self.login_url,
            {'username': 'test_user', 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        refresh_response = self.client.post(
            self.refresh_url,
            {'refresh': response.data['refresh']},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        user = self.create_user()
        self.authenticate()

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['username'], 'test_user')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['role'], User.Role.USER)
        self.assertTrue(response.data['is_active'])

    def test_user_can_update_own_username_and_email(self):
        user = self.create_user()
        self.authenticate()

        response = self.client.patch(
            self.me_url,
            {'username': 'renamed_user', 'email': 'updated@example.com'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'renamed_user')
        self.assertEqual(response.data['email'], 'updated@example.com')
        user.refresh_from_db()
        self.assertEqual(user.username, 'renamed_user')
        self.assertEqual(user.email, 'updated@example.com')

    def test_user_cannot_update_to_existing_username(self):
        self.create_user(username='test_user')
        self.create_user(username='other_user', email='other@example.com')
        self.authenticate()

        response = self.client.patch(
            self.me_url,
            {'username': 'OTHER_USER'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_can_deactivate_own_account(self):
        self.create_user()
        tokens = self.authenticate()

        response = self.client.delete(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.get(username='test_user').is_active)

        self.client.credentials()
        login_response = self.client.post(
            self.login_url,
            {'username': 'test_user', 'password': self.password},
            format='json',
        )
        refresh_response = self.client.post(
            self.refresh_url,
            {'refresh': tokens['refresh']},
            format='json',
        )
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_change_password(self):
        self.create_user()
        self.authenticate()

        response = self.client.post(
            self.password_url,
            {
                'old_password': self.password,
                'new_password': 'NewStrongPass123!',
                'confirm_password': 'NewStrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(username='test_user')
        self.assertTrue(user.check_password('NewStrongPass123!'))

    def test_password_change_rejects_invalid_old_password(self):
        self.create_user()
        self.authenticate()

        response = self.client.post(
            self.password_url,
            {
                'old_password': 'WrongPassword123!',
                'new_password': 'NewStrongPass123!',
                'confirm_password': 'NewStrongPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_password_change_rejects_mismatched_confirmation(self):
        self.create_user()
        self.authenticate()

        response = self.client.post(
            self.password_url,
            {
                'old_password': self.password,
                'new_password': 'NewStrongPass123!',
                'confirm_password': 'DifferentPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_public_user_profile_and_likes_are_read_only(self):
        user = self.create_user()
        category = Category.objects.create(name='用户主页测试')
        article = Article.objects.create(
            title='用户主页文章',
            content={'format': 'markdown', 'body': '正文'},
            author=user,
            category=category,
        )
        Like.objects.create(article=article, user=user)
        self.authenticate()

        profile_response = self.client.get(f'/api/users/{user.id}/')
        likes_response = self.client.get(f'/api/users/{user.id}/likes/')
        update_response = self.client.patch(
            f'/api/users/{user.id}/',
            {'username': '越权修改'},
            format='json',
        )

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['username'], user.username)
        self.assertEqual(likes_response.status_code, status.HTTP_200_OK)
        self.assertEqual(likes_response.data['results'][0]['id'], article.id)
        self.assertEqual(update_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_can_upload_jpg_or_png_avatar_under_three_mb(self):
        user = self.create_user()
        self.authenticate()
        image_buffer = BytesIO()
        Image.new('RGB', (20, 20), 'blue').save(image_buffer, format='PNG')
        upload = SimpleUploadedFile(
            'avatar.png',
            image_buffer.getvalue(),
            content_type='image/png',
        )

        response = self.client.post(
            '/api/auth/avatar/',
            {'avatar': upload},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.avatar.name.startswith('avatars/'))
        self.assertIsNotNone(response.data['avatar_url'])
        user.avatar.delete(save=False)

    def test_avatar_upload_rejects_non_image_file(self):
        self.create_user()
        self.authenticate()
        upload = SimpleUploadedFile(
            'avatar.gif',
            b'not-an-image',
            content_type='image/gif',
        )

        response = self.client.post(
            '/api/auth/avatar/',
            {'avatar': upload},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('avatar', response.data)
