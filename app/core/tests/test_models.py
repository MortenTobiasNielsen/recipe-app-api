from django.test import TestCase
from django.contrib.auth import get_user_model

import app.utils as utils


class ModelTests(TestCase):

    def setUp(self):
        self.user = utils.create_user(**utils.USER_PAYLOAD)
        self.superuser = utils.create_superuser(**utils.SUPERUSER_PAYLOAD)

    def test_create_user_with_email_succcesfull(self):
        """Test creating a new user with an email is successfull"""
        self.assertEqual(self.user.email, utils.USER_PAYLOAD["email"])
        self.assertTrue(self.user.check_password(
            utils.USER_PAYLOAD["password"]))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "normalizedtest@TEsT.COM"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        self.assertTrue(self.superuser.is_superuser)
        self.assertTrue(self.superuser.is_staff)

    def test_tag_str(self):
        """Test the tag string represention"""
        tag = utils.create_tag(self.user, "Vegan")

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = utils.create_ingredent(self.user, "Cabbage")

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string represention"""
        recipe = utils.create_recipe(
            self.user,
            "Steak and mushroom sauce",
            5,
            5.00,
        )
        self.assertEqual(str(recipe), recipe.title)
