from copy import deepcopy

import tempfile
import os

from PIL import Image

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

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        res = self.client.post(utils.RECIPES_URL, utils.RECIPE_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])

        for key in utils.RECIPE_PAYLOAD.keys():
            self.assertEqual(utils.RECIPE_PAYLOAD[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = utils.create_tag(self.user, "Vegan")
        tag2 = utils.create_tag(self.user, "Dessert")
        payload = deepcopy(utils.RECIPE_PAYLOAD)
        payload.update({"tags": [tag1.id, tag2.id]})
        res = self.client.post(utils.RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ingredient1 = utils.create_ingredent(self.user, "Prawns")
        ingredient2 = utils.create_ingredent(self.user, "Ginger")
        payload = deepcopy(utils.RECIPE_PAYLOAD)
        payload.update({"ingredients": [ingredient1.id, ingredient2.id]})
        res = self.client.post(utils.RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = utils.create_recipe(self.user)
        recipe.tags.add(utils.create_tag(self.user, "Spicy"))
        new_tag = utils.create_tag(self.user, "Curry")

        payload = deepcopy(utils.RECIPE_PAYLOAD)
        payload.update({"tags": [new_tag.id]})

        url = utils.recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = utils.create_recipe(self.user)
        recipe.tags.add(utils.create_tag(self.user, "Spicy"))
        url = utils.recipe_detail_url(recipe.id)
        payload = deepcopy(utils.RECIPE_PAYLOAD)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.time_minutes, payload["time_minutes"])
        self.assertEqual(recipe.price, payload["price"])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = utils.create_user(**utils.USER_PAYLOAD)
        self.client.force_authenticate(self.user)
        self.recipe = utils.create_recipe(self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test updading an image to recipe"""
        url = utils.image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = utils.image_upload_url(self.recipe.id)
        res = self.client.post(url, {"image": "notimage"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Test returning recipes with specific tags"""
        recipe1 = utils.create_recipe(self.user)
        recipe2 = utils.create_recipe(self.user)
        recipe3 = utils.create_recipe(self.user)

        tag1 = utils.create_tag(self.user, "Vegan")
        tag2 = utils.create_tag(self.user, "Vegetatian")

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        res = self.client.get(
            utils.RECIPES_URL,
            {"tags": f"{tag1.id}, {tag2.id}"},
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test returning recipes with specific ingredients"""
        recipe1 = utils.create_recipe(self.user)
        recipe2 = utils.create_recipe(self.user)
        recipe3 = utils.create_recipe(self.user)

        ingredient1 = utils.create_ingredent(self.user, "Salt")
        ingredient2 = utils.create_ingredent(self.user, "Pepper")

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        res = self.client.get(
            utils.RECIPES_URL,
            {"ingredients": f"{ingredient1.id}, {ingredient2.id}"}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
