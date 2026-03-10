import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from recipes.models import Tag, Ingredient, Recipe


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_tag_list_returns_200(client):
    """GET /api/tags/ возвращает 200"""
    response = client.get('/api/tags/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_ingredient_list_returns_200(client):
    """GET /api/ingredients/ возвращает 200"""
    response = client.get('/api/ingredients/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_recipe_list_returns_200(client):
    """GET /api/recipes/ возвращает 200"""
    response = client.get('/api/recipes/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_tag_created_successfully():
    """Тег создаётся и сохраняется в БД"""
    tag = Tag.objects.create(name='Завтрак', color='#FF0000', slug='zavtrak')
    assert Tag.objects.count() == 1
    assert tag.name == 'Завтрак'


@pytest.mark.django_db
def test_ingredient_created_successfully():
    """Ингредиент создаётся и сохраняется в БД"""
    ingredient = Ingredient.objects.create(name='Соль', measurement_unit='г')
    assert Ingredient.objects.count() == 1
    assert ingredient.measurement_unit == 'г'


@pytest.mark.django_db
def test_recipe_list_is_empty(client):
    """GET /api/recipes/ возвращает пустой список"""
    response = client.get('/api/recipes/')
    assert response.status_code == 200
    assert response.data['results'] == []