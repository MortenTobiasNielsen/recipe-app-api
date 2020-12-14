from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

import app.utils as utils


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(utils.TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = utils.create_user(**utils.USER_PAYLOAD)
        self.user2 = utils.create_user(**utils.USER_PAYLOAD_UPDATE)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        utils.create_tag(self.user, "Vegan")
        utils.create_tag(self.user, "Dessert")

        res = self.client.get(utils.TAGS_URL)

        serializer = TagSerializer(utils.all_tags(), many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        tag = utils.create_tag(self.user, "Comfort food")
        utils.create_tag(self.user2, "Fruity")

        res = self.client.get(utils.TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_create_tag_successful(self):
        """Test create a new tag"""
        payload = {"name": "Test_tag"}
        self.client.post(utils.TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {"name": ""}
        res = self.client.post(utils.TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = utils.create_tag(self.user, "Vegan")
        tag2 = utils.create_tag(self.user, "Lunch")

        recipe = utils.create_recipe(self.user)
        recipe.tags.add(tag1)

        res = self.client.get(utils.TAGS_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = utils.create_tag(self.user, "Vegan")
        utils.create_tag(self.user, "Lunch")

        recipe1 = utils.create_recipe(self.user, **utils.RECIPE_PAYLOAD)
        recipe2 = utils.create_recipe(self.user, **utils.RECIPE_PAYLOAD_UPDATE)

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(utils.TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
