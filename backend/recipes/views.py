from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

from .models import Tag, Ingredient, Recipe, ShoppingCart
from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeWriteSerializer,
    ShoppingCartSerializer
)
from .filters import RecipeFilter


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientListView(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeListCreateView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.query_params.get('user_id')
        return context


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.query_params.get('user_id')
        return context


class ShoppingCartView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id', 0)
        items = ShoppingCart.objects.filter(user_id=user_id)
        serializer = ShoppingCartSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, recipe_id):
        user_id = request.data.get('user_id', 0)
        recipe = generics.get_object_or_404(Recipe, id=recipe_id)
        item, created = ShoppingCart.objects.get_or_create(
            user_id=user_id, recipe=recipe
        )
        if not created:
            return Response(
                {'detail': 'Рецепт уже в корзине.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ShoppingCartSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user_id = request.data.get('user_id', 0)
        item = generics.get_object_or_404(
            ShoppingCart, user_id=user_id, recipe_id=recipe_id
        )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartDownloadView(APIView):
    def get(self, request):
        import os
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        user_id = request.query_params.get('user_id', 0)
        items = ShoppingCart.objects.filter(
            user_id=user_id
        ).select_related('recipe')

        ingredients_summary = {}
        for cart_item in items:
            for ri in cart_item.recipe.recipe_ingredients.select_related('ingredient'):
                key = f'{ri.ingredient.name} ({ri.ingredient.measurement_unit})'
                ingredients_summary[key] = ingredients_summary.get(key, 0) + ri.amount

        # Подключаем шрифт с кириллицей
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        p.setFont('DejaVu', 16)
        p.drawString(50, 800, 'Список покупок')
        p.setFont('DejaVu', 12)

        y = 770
        for name, amount in ingredients_summary.items():
            p.drawString(50, y, f'- {name}: {amount}')
            y -= 20
            if y < 50:
                p.showPage()
                p.setFont('DejaVu', 12)
                y = 800

        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
        return response