from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(source='recipe_ingredients', many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return ""

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(child=serializers.DictField(), write_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'image', 'name', 'text', 'cooking_time')

    def validate_cooking_time(self, value):
        if value <= 1:
            raise serializers.ValidationError("cooking_time должно быть >= 1.")
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Поле 'image' не может быть пустым.")
        return value

    def validate_ingredients(self, value):
        if value is None:
            raise serializers.ValidationError("Поле 'ingredients' является обязательным.")
        if not value:
            raise serializers.ValidationError("Поле 'ingredients' не может быть пустым.")
        ingredient_ids = [ingredient["id"] for ingredient in value]
        existing_ingredients = set(Ingredient.objects.filter(id__in=ingredient_ids).values_list("id", flat=True))

        missing_ingredients = [ingredient_id for ingredient_id in ingredient_ids if
                               ingredient_id not in existing_ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError("Ингредиенты не должны повторяться.")
        if missing_ingredients:
            raise serializers.ValidationError(f"Некоторые ингредиенты не существуют: {missing_ingredients}")
        for ingredient in value:
            if int(ingredient["amount"]) <= 1:
                raise serializers.ValidationError(f"Количество ингредиента (id {ingredient['id']}) должно быть >= 1.")

        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)

        if ingredients_data is None:
            raise serializers.ValidationError(
                {"ingredients": "Поле 'ingredients' является обязательным при обновлении рецепта."})

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        instance.recipe_ingredients.all().delete()
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )

        return instance
