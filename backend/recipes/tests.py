import io
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Tag, Ingredient, Recipe, RecipeIngredient, ShoppingCart


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def tag():
    return Tag.objects.create(name='Завтрак', color='#FF0000', slug='breakfast')


@pytest.fixture
def ingredient():
    return Ingredient.objects.create(name='Яйцо', measurement_unit='шт')


@pytest.fixture
def recipe(tag, ingredient):
    r = Recipe.objects.create(
        author_id=1,
        name='Яичница',
        text='Просто пожарить яйца',
        cooking_time=5
    )
    r.tags.set([tag])
    RecipeIngredient.objects.create(recipe=r, ingredient=ingredient, amount=2)
    return r


# теги

@pytest.mark.django_db
def test_tag_list(client, tag):
    response = client.get('/api/tags/')
    assert response.status_code == 200
    assert response.data['count'] == 1


@pytest.mark.django_db
def test_tag_fields(client, tag):
    response = client.get('/api/tags/')
    result = response.data['results'][0]
    assert result['name'] == 'Завтрак'
    assert result['slug'] == 'breakfast'


# ингредиенты

@pytest.mark.django_db
def test_ingredient_list(client, ingredient):
    response = client.get('/api/ingredients/')
    assert response.status_code == 200
    assert response.data['count'] == 1


@pytest.mark.django_db
def test_ingredient_fields(client, ingredient):
    response = client.get('/api/ingredients/')
    result = response.data['results'][0]
    assert result['name'] == 'Яйцо'
    assert result['measurement_unit'] == 'шт'


# рецепты

@pytest.mark.django_db
def test_recipe_list(client, recipe):
    response = client.get('/api/recipes/')
    assert response.status_code == 200
    assert response.data['count'] == 1


@pytest.mark.django_db
def test_recipe_detail(client, recipe):
    response = client.get(f'/api/recipes/{recipe.id}/')
    assert response.status_code == 200
    assert response.data['name'] == 'Яичница'


@pytest.mark.django_db
def test_recipe_detail_has_ingredients(client, recipe):
    response = client.get(f'/api/recipes/{recipe.id}/')
    assert 'ingredients' in response.data
    assert len(response.data['ingredients']) == 1
    assert response.data['ingredients'][0]['name'] == 'Яйцо'
    assert response.data['ingredients'][0]['amount'] == 2


@pytest.mark.django_db
def test_recipe_detail_has_tags(client, recipe):
    response = client.get(f'/api/recipes/{recipe.id}/')
    assert 'tags' in response.data
    assert response.data['tags'][0]['slug'] == 'breakfast'


@pytest.mark.django_db
def test_recipe_create(client, tag, ingredient):
    data = {
        'author_id': 1,
        'name': 'Омлет',
        'text': 'Взбить яйца и пожарить',
        'cooking_time': 10,
        'tags': [tag.id],
        'ingredients': [{'id': ingredient.id, 'amount': 3}]
    }
    response = client.post('/api/recipes/', data, format='json')
    assert response.status_code == 201
    assert Recipe.objects.filter(name='Омлет').exists()


@pytest.mark.django_db
def test_recipe_create_ingredients_saved(client, tag, ingredient):
    data = {
        'author_id': 1,
        'name': 'Омлет',
        'text': 'Взбить яйца',
        'cooking_time': 10,
        'tags': [tag.id],
        'ingredients': [{'id': ingredient.id, 'amount': 3}]
    }
    client.post('/api/recipes/', data, format='json')
    recipe = Recipe.objects.get(name='Омлет')
    assert RecipeIngredient.objects.filter(recipe=recipe, amount=3).exists()


@pytest.mark.django_db
def test_recipe_patch(client, recipe, tag, ingredient):
    data = {
        'name': 'Яичница обновлённая',
        'text': 'Новое описание',
        'cooking_time': 7,
        'tags': [tag.id],
        'ingredients': [{'id': ingredient.id, 'amount': 4}]
    }
    response = client.patch(f'/api/recipes/{recipe.id}/', data, format='json')
    assert response.status_code == 200
    recipe.refresh_from_db()
    assert recipe.name == 'Яичница обновлённая'


@pytest.mark.django_db
def test_recipe_delete(client, recipe):
    response = client.delete(f'/api/recipes/{recipe.id}/')
    assert response.status_code == 204
    assert not Recipe.objects.filter(id=recipe.id).exists()


# корзина

@pytest.mark.django_db
def test_shopping_cart_add(client, recipe):
    response = client.post(
        f'/api/shopping_cart/{recipe.id}/',
        {'user_id': 1},
        format='json'
    )
    assert response.status_code == 201
    assert ShoppingCart.objects.filter(user_id=1, recipe=recipe).exists()


@pytest.mark.django_db
def test_shopping_cart_list(client, recipe):
    ShoppingCart.objects.create(user_id=1, recipe=recipe)
    response = client.get('/api/shopping_cart/?user_id=1')
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_shopping_cart_duplicate(client, recipe):
    ShoppingCart.objects.create(user_id=1, recipe=recipe)
    response = client.post(
        f'/api/shopping_cart/{recipe.id}/',
        {'user_id': 1},
        format='json'
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_shopping_cart_delete(client, recipe):
    ShoppingCart.objects.create(user_id=1, recipe=recipe)
    response = client.delete(
        f'/api/shopping_cart/{recipe.id}/',
        {'user_id': 1},
        format='json'
    )
    assert response.status_code == 204
    assert not ShoppingCart.objects.filter(user_id=1, recipe=recipe).exists()


@pytest.mark.django_db
def test_shopping_cart_download(client, recipe):
    ShoppingCart.objects.create(user_id=1, recipe=recipe)
    response = client.get('/api/shopping_cart/download/?user_id=1')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'


# фильтры

@pytest.mark.django_db
def test_filter_by_tag(client, recipe, tag):
    response = client.get(f'/api/recipes/?tags={tag.id}')
    assert response.status_code == 200
    assert response.data['count'] == 1


@pytest.mark.django_db
def test_filter_shopping_cart(client, recipe):
    ShoppingCart.objects.create(user_id=1, recipe=recipe)
    response = client.get('/api/recipes/?is_in_shopping_cart=1&user_id=1')
    assert response.status_code == 200
    assert response.data['count'] == 1