import django_filters
from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.BaseInFilter(
        field_name='tags__id',
        lookup_expr='in'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'is_in_shopping_cart']

    def filter_shopping_cart(self, queryset, name, value):
        user_id = self.request.query_params.get('user_id')
        if value == 1 and user_id:
            return queryset.filter(in_shopping_cart__user_id=user_id)
        return queryset