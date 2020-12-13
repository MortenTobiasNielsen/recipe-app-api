from django.test import TestCase, Client

import app.utils as utils


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = utils.create_superuser(**utils.ADMIN_PAYLOAD)
        self.client.force_login(self.admin_user)
        self.user = utils.create_user(**utils.USER_PAYLOAD)

    def test_users_listed(self):
        """Test that users are listed on user page"""
        res = self.client.get(utils.ADMIN_CHANGE_URL)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        res = self.client.get(utils.admin_detail_url(self.user.id))

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        res = self.client.get(utils.ADMIN_CHANGE_URL)

        self.assertEqual(res.status_code, 200)
