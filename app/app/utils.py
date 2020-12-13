from django.contrib.auth import get_user_model
from django.urls import reverse

from core import models

INGREDIENTS_URL = reverse("recipe:ingredient-list")
CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")
TAGS_URL = reverse("recipe:tag-list")
ADMIN_CHANGE_URL = reverse("admin:core_user_changelist")

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


def create_recipe(user, title, time, price):
    return models.Recipe.objects.create(
        user=user,
        title=title,
        time_minutes=time,
        price=price,
    )
