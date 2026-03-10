from rest_framework import serializers
from .models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'author_id', 'name', 'image', 'text', 'tags', 'cooking_time', 'pub_date']
