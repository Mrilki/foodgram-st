from collections import defaultdict

from django.http import HttpResponse
from django_filters.rest_framework import FilterSet, CharFilter, BooleanFilter, DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, status, generics
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Recipe, Favorite, Ingredient
from .models import ShoppingCart
from .permissions import IsAuthorOrReadOnly
from .serializers import RecipeListSerializer, RecipeCreateSerializer, RecipeMinifiedSerializer, IngredientSerializer


class RecipeFilter(FilterSet):
    author = CharFilter(field_name='author__id', lookup_expr="iexact")
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author']

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset

        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset.exclude(shopping_cart__user=user)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        if value:
            return queryset.filter(favorites__user=user)
        return queryset.exclude(favorites__user=user)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = f"https://foodgram.example.org/s/{recipe.id}"
        return Response({"short-link": short_link})

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            obj, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response({'error': 'Рецепт уже в избранном.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeMinifiedSerializer(recipe, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:  # DELETE
            try:
                favorite = Favorite.objects.get(user=request.user, recipe=recipe)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response({'error': 'Рецепта нет в избранном.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            obj, created = ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response({'error': 'Рецепт уже в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeMinifiedSerializer(recipe, context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:  # DELETE
            try:
                cart_item = ShoppingCart.objects.get(user=request.user, recipe=recipe)
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response({'error': 'Рецепта нет в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    # Собираем ингредиенты для всех рецептов из списка покупок текущего пользователя.
    ingredients = defaultdict(lambda: 0)
    cart_items = ShoppingCart.objects.filter(user=request.user).select_related('recipe')
    # Проходим по каждому рецепту и суммируем ингредиенты.
    for cart_item in cart_items:
        for ri in cart_item.recipe.recipe_ingredients.all():
            key = (ri.ingredient.name, ri.ingredient.measurement_unit)
            ingredients[key] += ri.amount

    # Формируем текстовый файл: каждая строка — "Ингредиент (единица измерения) — общее количество"
    lines = [f"{name} ({unit}) — {amount}" for (name, unit), amount in ingredients.items()]
    content = "\n".join(lines)

    response = HttpResponse(content, content_type="text/plain")
    response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
    return response


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class IngredientListView(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientDetailView(generics.RetrieveAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
