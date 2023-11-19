from django.contrib import admin
from .models import Category, Product, Color, ProductImage, ProductColor, ProductReview

# Register the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image','is_active', 'is_featured', 'created_at', 'updated_at')
    list_filter = ('is_active', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

# Register the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'is_featured', 'created_at', 'updated_at')
    list_filter = ('is_active', 'is_featured', 'category')
    search_fields = ('title', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}

# Register the Color model
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'is_active')
    list_filter = ('color',)
    
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product_color','image')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display=('user','product', 'rating', 'review_text')