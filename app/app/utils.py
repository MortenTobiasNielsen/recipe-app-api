from django.contrib.auth import get_user_model
from django.urls import reverse

from core import models

ADMIN_CHANGE_URL = reverse("admin:core_user_changelist")
INGREDIENTS_URL = reverse("recipe:ingredient-list")
CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")
TAGS_URL = reverse("recipe:tag-list")
RECIPES_URL = reverse("recipe:recipe-list")

ADMIN_PAYLOAD = {
    "email": "admin@test.com",
    "password": "password123"
}

SUPERUSER_PAYLOAD = {
    "email": "super@test.com",
    "password": "minpass123",
}

USER_PAYLOAD = {
    "email": "test@test.com",
    "password": "minpass123",
    "name": "Testing"
}

USER_PAYLOAD_UPDATE = {
    "email": "test_update@test.com",
    "password": "minpass1234",
    "name": "Testing Update"
}

USER_PAYLOAD_WRONG = {
    "email": "wrong@test.com",
    "password": "wrong",
    "name": "Testing"
}

RECIPE_PAYLOAD = {
    "title": "chocolate cake",
    "time_minutes": 30,
    "price": 5.00,
}

RECIPE_PAYLOAD_UPDATE = {
    "title": "chocolate muffin",
    "time_minutes": 25,
    "price": 10.00,
}


def recipe_detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


def admin_detail_url(user_id):
    return reverse("admin:core_user_change", args=[user_id])


def create_superuser(**params):
    return get_user_model().objects.create_superuser(**params)


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_ingredent(user, name):
    return models.Ingredient.objects.create(
        user=user,
        name=name,
    )


def all_ingredients():
    return models.Ingredient.objects.all().order_by("-name")


def create_tag(user, name):
    return models.Tag.objects.create(
        user=user,
        name=name,
    )


def all_tags():
    return models.Tag.objects.all().order_by("-name")


def create_recipe(user, **params):
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 10,
        "price": 5.00,
    }
    defaults.update(params)

    return models.Recipe.objects.create(user=user, **defaults)


def all_recipes():
    return models.Recipe.objects.all().order_by("-id")
