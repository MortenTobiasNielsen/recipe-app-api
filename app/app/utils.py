from django.contrib.auth import get_user_model
from django.urls import reverse


INGREDIENTS_URL = reverse("recipe:ingredient-list")
CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

PAYLOAD = {
    "email": "test@test.com",
    "password": "minpass123",
    "name": "Testing"
}

PAYLOAD_UPDATE = {
    "email": "test_update@test.com",
    "password": "minpass1234",
    "name": "Testing Update"
}

PAYLOAD_WRONG = {
    "email": "test@test.com",
    "password": "wrong",
    "name": "Testing"
}


def sample_user(email="test@test.com", password="password123"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)
