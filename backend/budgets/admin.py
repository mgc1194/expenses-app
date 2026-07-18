from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'household', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'household')
    search_fields = ('name',)
    raw_id_fields = ('household',)
