from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import CustomUser, Subscription


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(subscriber=request.user, author=obj).exists()
        return False


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserWithRecipesSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit') if request else None
        queryset = obj.recipes.all()
        if recipes_limit is not None:
            try:
                limit = int(recipes_limit)
                queryset = queryset[:limit]
            except ValueError:
                pass
        from recipes.serializers import RecipeMinifiedSerializer
        serializer = RecipeMinifiedSerializer(queryset, many=True, context=self.context)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import Subscription
            return Subscription.objects.filter(subscriber=request.user, author=obj).exists()
        return False


class SetAvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
