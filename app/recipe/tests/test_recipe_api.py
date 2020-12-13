from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

import app.utils as utils


class PublicRecipeApiTests(TestCase):
    """Test the publicly available recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(utils.RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the authorized user recipe API"""

    def setUp(self):
        self.client = APIClient()
        self.user = utils.create_user(**utils.USER_PAYLOAD)
        self.user2 = utils.create_user(**utils.USER_PAYLOAD_UPDATE)
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrieving a list of recipes"""
        utils.create_recipe(self.user)
        utils.create_recipe(self.user)

        res = self.client.get(utils.RECIPES_URL)

        serializer = RecipeSerializer(utils.all_recipes(), many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        utils.create_recipe(self.user)
        utils.create_recipe(self.user2)

        res = self.client.get(utils.RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detial"""
        recipe = utils.create_recipe(self.user)
        recipe.tags.add(utils.create_tag(self.user, "Vegan"))
        recipe.ingredients.add(utils.create_ingredent(self.user, "Salt"))

        res = self.client.get(utils.recipe_detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)
