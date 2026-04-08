from rest_framework import serializers
from .models import Tag, Ingredient, Recipe, RecipeIngredient, ShoppingCart


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'author_id', 'name', 'image', 'text',
            'tags', 'ingredients', 'cooking_time',
            'pub_date', 'is_in_shopping_cart'
        ]

    def get_is_in_shopping_cart(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            return False
        return ShoppingCart.objects.filter(user_id=user_id, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True, write_only=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'author_id', 'name', 'image', 'text',
            'tags', 'ingredients', 'cooking_time'
        ]

    def to_internal_value(self, data):
        import json
        if isinstance(data.get('ingredients'), str):
            try:
                data = data.copy()
                data['ingredients'] = json.loads(data['ingredients'])
            except (ValueError, TypeError):
                pass
        return super().to_internal_value(data)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for item in ingredients_data:
            ingredient = Ingredient.objects.get(id=item['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=item['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            for item in ingredients_data:
                ingredient = Ingredient.objects.get(id=item['id'])
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=item['amount']
                )
        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe_name = serializers.CharField(source='recipe.name', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time', read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ['id', 'recipe', 'recipe_name', 'cooking_time']