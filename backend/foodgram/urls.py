from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipes.views import (
    RecipeViewSet,
    download_shopping_cart,
    IngredientListView,
    IngredientDetailView
)
from users.views import (
    CustomUserListCreateView,
    CurrentUserView,
    SubscriptionListView,
    SubscribeView,
    UserDetailView,
    UserAvatarView,
    SetPasswordView
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
                  path('admin/', admin.site.urls),
                  # Пользователи:
                  path('api/users/', CustomUserListCreateView.as_view(), name='users'),
                  path('api/users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
                  path('api/users/me/', CurrentUserView.as_view(), name='current_user'),
                  path('api/users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
                  path('api/users/set_password/', SetPasswordView.as_view(), name='set-password'),
                  path('api/users/subscriptions/', SubscriptionListView.as_view(), name='subscriptions'),
                  path('api/users/<int:id>/subscribe/', SubscribeView.as_view(), name='subscribe'),

                  # Рецепты:
                  path('api/recipes/download_shopping_cart/', download_shopping_cart, name='download_shopping_cart'),
                  path('api/', include(router.urls)),
                  path('api/ingredients/', IngredientListView.as_view(), name='ingredients'),
                  path('api/ingredients/<int:pk>/', IngredientDetailView.as_view(), name='ingredient-detail'),

                  # Аутентификация через djoser:
                  path('api/auth/', include('djoser.urls')),
                  path('api/auth/', include('djoser.urls.authtoken')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
