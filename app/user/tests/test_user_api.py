from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

import app.utils as utils


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successfull"""
        res = self.client.post(utils.CREATE_USER_URL, utils.USER_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(utils.USER_PAYLOAD["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        utils.create_user(**utils.USER_PAYLOAD)

        res = self.client.post(utils.CREATE_USER_URL, utils.USER_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be at least 10 characters"""
        res = self.client.post(utils.CREATE_USER_URL, utils.USER_PAYLOAD_WRONG)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=utils.USER_PAYLOAD["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        create_user(**utils.USER_PAYLOAD)
        res = self.client.post(utils.TOKEN_URL, utils.USER_PAYLOAD)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(**utils.USER_PAYLOAD)
        res = self.client.post(utils.TOKEN_URL, utils.USER_PAYLOAD_WRONG)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        res = self.client.post(utils.TOKEN_URL, utils.USER_PAYLOAD)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(utils.TOKEN_URL, utils.USER_PAYLOAD_WRONG)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unautorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(utils.ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(**utils.USER_PAYLOAD)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_sucess(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(utils.ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "name": self.user.name,
            "email": self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(utils.ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        res = self.client.patch(utils.ME_URL, utils.USER_PAYLOAD_UPDATE)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, utils.USER_PAYLOAD_UPDATE["name"])
        self.assertTrue(self.user.check_password(
            utils.USER_PAYLOAD_UPDATE["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_password_too_short_update(self):
        """Test that the password must be at least 10 characters on update"""
        res = self.client.patch(utils.ME_URL, utils.USER_PAYLOAD_WRONG)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.put(utils.ME_URL, utils.USER_PAYLOAD_WRONG)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
