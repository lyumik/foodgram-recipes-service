from django.urls import path
from . import views

urlpatterns = [
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('ingredients/', views.IngredientListView.as_view(), name='ingredient-list'),
    path('recipes/', views.RecipeListCreateView.as_view(), name='recipe-list'),
    path('recipes/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe-detail'),
    path('shopping_cart/', views.ShoppingCartView.as_view(), name='shopping-cart'),
    path('shopping_cart/download/', views.ShoppingCartDownloadView.as_view(), name='shopping-cart-download'),
    path('shopping_cart/<int:recipe_id>/', views.ShoppingCartView.as_view(), name='shopping-cart-item'),
]