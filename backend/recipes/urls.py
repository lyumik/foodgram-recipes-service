from django.urls import path
from . import views

urlpatterns = [
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('ingredients/', views.IngredientListView.as_view(), name='ingredient-list'),
    path('recipes/', views.RecipeListView.as_view(), name='recipe-list'),
]