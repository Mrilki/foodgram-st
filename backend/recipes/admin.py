from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'cooking_time', 'created', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')

    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = 'Кол-во избранных'

admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)