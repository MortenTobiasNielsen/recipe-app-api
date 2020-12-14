from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

import app.utils as utils


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(utils.INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the privitely available ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = utils.create_user(**utils.USER_PAYLOAD)
        self.user2 = utils.create_user(**utils.USER_PAYLOAD_UPDATE)
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        utils.create_ingredent(self.user, "Kale")
        utils.create_ingredent(self.user, "Salt")

        res = self.client.get(utils.INGREDIENTS_URL)

        serializer = IngredientSerializer(utils.all_ingredients(), many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated user are returned"""
        utils.create_ingredent(self.user2, "Vinegar")
        ingredient = utils.create_ingredent(self.user, "Tumeric")

        res = self.client.get(utils.INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_create_ingredients_success(self):
        """Test create a new ingredient"""
        payload = {"name": "Cabbage"}
        self.client.post(utils.INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload["name"],
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredients_invalid(self):
        """Test creating a new ingredient with invalid payload"""
        payload = {"name": ""}
        res = self.client.post(utils.INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = utils.create_ingredent(self.user, "Appels")
        ingredient2 = utils.create_ingredent(self.user, "Turkey")

        recipe = utils.create_recipe(self.user, **utils.RECIPE_PAYLOAD)
        recipe.ingredients.add(ingredient1)

        res = self.client.get(utils.INGREDIENTS_URL, {"assigned_only": 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = utils.create_ingredent(self.user, "Appels")
        utils.create_ingredent(self.user, "Turkey")

        recipe1 = utils.create_recipe(self.user, **utils.RECIPE_PAYLOAD)
        recipe2 = utils.create_recipe(self.user, **utils.RECIPE_PAYLOAD_UPDATE)

        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res = self.client.get(utils.INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
