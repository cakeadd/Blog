from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article, Category
from comments.models import Comment


User = get_user_model()


class AdministrationApiTests(APITestCase):
    password = 'StrongPass123!'

    def setUp(self):
        self.admin = User.objects.create_user(
            username='blog_admin',
            password=self.password,
            role=User.Role.ADMIN,
        )
        self.user = User.objects.create_user(
            username='normal_user',
            password=self.password,
        )
        self.category = Category.objects.create(name='管理测试')
        self.article = Article.objects.create(
            title='管理测试文章',
            content={'format': 'markdown', 'body': '正文'},
            author=self.user,
            category=self.category,
        )
        self.comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='管理测试评论',
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

    def test_non_admin_cannot_access_management_endpoint(self):
        self.authenticate(self.user)

        response = self.client.delete(f'/api/admin/articles/{self.article.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_deleted)

    def test_admin_cannot_use_normal_user_mutation_endpoint(self):
        self.authenticate(self.admin)

        response = self.client.patch(
            '/api/auth/me/',
            {'username': 'changed_admin_name'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_article_list_paginates_and_includes_deleted_articles(self):
        for index in range(5):
            Article.objects.create(
                title=f'文章列表 {index}',
                content={'format': 'markdown', 'body': '正文'},
                author=self.user,
                category=self.category,
            )
        deleted_article = Article.objects.create(
            title='已删除文章',
            content={'format': 'markdown', 'body': '正文'},
            author=self.user,
            category=self.category,
            is_deleted=True,
        )
        self.authenticate(self.admin)

        response = self.client.get('/api/admin/articles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)
        self.assertEqual(len(response.data['results']), 5)
        second_page = self.client.get('/api/admin/articles/?page=2')
        all_ids = {
            item['id']
            for item in response.data['results'] + second_page.data['results']
        }
        self.assertIn(deleted_article.id, all_ids)

    def test_admin_article_search_supports_fuzzy_and_exact_id_matching(self):
        self.authenticate(self.admin)

        fuzzy_response = self.client.get(
            '/api/admin/articles/',
            {'search': '测试文章'},
        )
        exact_response = self.client.get(
            '/api/admin/articles/',
            {'id': self.article.id},
        )

        self.assertEqual(fuzzy_response.status_code, status.HTTP_200_OK)
        self.assertEqual(fuzzy_response.data['count'], 1)
        self.assertEqual(exact_response.data['count'], 1)
        self.assertEqual(exact_response.data['results'][0]['id'], self.article.id)

    def test_admin_comment_list_includes_deleted_comments_and_supports_search(self):
        for index in range(5):
            Comment.objects.create(
                article=self.article,
                author=self.user,
                content=f'评论列表 {index}',
            )
        deleted_comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='已删除的评论',
            is_deleted=True,
        )
        self.authenticate(self.admin)

        paginated_response = self.client.get('/api/admin/comments/')
        fuzzy_response = self.client.get(
            '/api/admin/comments/',
            {'search': 'normal_user'},
        )
        exact_response = self.client.get(
            '/api/admin/comments/',
            {'id': self.comment.id},
        )

        self.assertEqual(paginated_response.status_code, status.HTTP_200_OK)
        self.assertEqual(paginated_response.data['count'], 7)
        self.assertEqual(len(paginated_response.data['results']), 5)
        second_page = self.client.get('/api/admin/comments/?page=2')
        all_ids = {
            item['id']
            for item in paginated_response.data['results'] + second_page.data['results']
        }
        self.assertIn(deleted_comment.id, all_ids)
        self.assertEqual(fuzzy_response.data['count'], 7)
        self.assertEqual(fuzzy_response.data['results'][0]['author_name'], self.user.username)
        self.assertEqual(exact_response.data['results'][0]['id'], self.comment.id)

    def test_admin_user_list_paginates_and_includes_inactive_users(self):
        inactive_user = User.objects.create_user(
            username='inactive_search_user',
            email='inactive@example.com',
            password=self.password,
            is_active=False,
        )
        for index in range(4):
            User.objects.create_user(
                username=f'list_user_{index}',
                password=self.password,
            )
        self.authenticate(self.admin)

        paginated_response = self.client.get('/api/admin/users/')
        search_response = self.client.get(
            '/api/admin/users/',
            {'search': 'inactive_search_user'},
        )
        exact_response = self.client.get(
            '/api/admin/users/',
            {'id': inactive_user.id},
        )

        self.assertEqual(paginated_response.status_code, status.HTTP_200_OK)
        self.assertEqual(paginated_response.data['count'], 6)
        self.assertEqual(len(paginated_response.data['results']), 5)
        self.assertEqual(search_response.data['count'], 1)
        self.assertFalse(search_response.data['results'][0]['is_active'])
        self.assertEqual(exact_response.data['results'][0]['id'], inactive_user.id)

    def test_admin_user_list_excludes_admin_accounts(self):
        self.authenticate(self.admin)

        response = self.client.get('/api/admin/users/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.admin.id, [item['id'] for item in response.data['results']])

    def test_admin_cannot_deactivate_or_restore_admin_account(self):
        self.authenticate(self.admin)

        deactivate_response = self.client.delete(
            f'/api/admin/users/{self.admin.id}/',
        )
        restore_response = self.client.patch(
            f'/api/admin/users/{self.admin.id}/restore/',
            {},
            format='json',
        )

        self.assertEqual(deactivate_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(restore_response.status_code, status.HTTP_404_NOT_FOUND)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_admin_can_delete_and_restore_article(self):
        self.authenticate(self.admin)

        delete_response = self.client.delete(
            f'/api/admin/articles/{self.article.id}/'
        )
        self.article.refresh_from_db()
        hidden_response = self.client.get(f'/api/articles/{self.article.id}/')
        restore_response = self.client.patch(
            f'/api/admin/articles/{self.article.id}/restore/',
            {},
            format='json',
        )

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(self.article.is_deleted)
        self.assertEqual(hidden_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(restore_response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_deleted)

    def test_admin_can_delete_and_restore_comment(self):
        self.authenticate(self.admin)

        delete_response = self.client.delete(
            f'/api/admin/comments/{self.comment.id}/'
        )
        self.comment.refresh_from_db()
        restore_response = self.client.patch(
            f'/api/admin/comments/{self.comment.id}/restore/',
            {},
            format='json',
        )

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(self.comment.is_deleted)
        self.assertEqual(restore_response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_deleted)

    def test_admin_can_deactivate_and_restore_user(self):
        self.authenticate(self.admin)

        deactivate_response = self.client.delete(
            f'/api/admin/users/{self.user.id}/'
        )
        self.user.refresh_from_db()
        self.client.credentials()
        login_response = self.client.post(
            '/api/auth/login/',
            {'username': self.user.username, 'password': self.password},
            format='json',
        )
        self.authenticate(self.admin)
        restore_response = self.client.patch(
            f'/api/admin/users/{self.user.id}/restore/',
            {},
            format='json',
        )

        self.assertEqual(deactivate_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.user.is_active)
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(restore_response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class AdminSetupApiTests(APITestCase):
    password = 'StrongPass123!'

    def test_admin_setup_status_is_uninitialized_at_first(self):
        response = self.client.get('/api/admin/setup/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['initialized'])

    def test_first_admin_setup_creates_admin(self):
        response = self.client.post(
            '/api/admin/setup/',
            {'username': 'first_admin', 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        admin = User.objects.get(username='first_admin')
        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertTrue(admin.check_password(self.password))

    def test_admin_setup_cannot_be_repeated(self):
        response = self.client.post(
            '/api/admin/setup/',
            {'username': 'another_admin', 'password': self.password},
            format='json',
        )
        second_response = self.client.post(
            '/api/admin/setup/',
            {'username': 'second_admin', 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(User.objects.filter(username='second_admin').exists())
