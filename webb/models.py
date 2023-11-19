from django.db import models
from django.contrib.auth.models import User
import uuid  # Import the uuid module
# from django.db.models import Sum
# from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=55, verbose_name="Category Slug")
    description = models.TextField(blank=True, verbose_name="Category Description")
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, verbose_name="Category Image") # category image
    is_active = models.BooleanField(verbose_name="Is Active?")
    is_featured = models.BooleanField(verbose_name="Is Featured?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('-created_at', )
        
    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Add other fields as needed
    slug = models.SlugField(max_length=160, verbose_name="Product Slug")
    sku = models.CharField(max_length=255, unique=True, verbose_name="Unique Product ID (SKU)")
    short_description = models.TextField(verbose_name="Short Description")
    detail_description = models.TextField(blank=True, null=True, verbose_name="Detail Description")
    is_active = models.BooleanField(verbose_name="Is Active?")
    is_featured = models.BooleanField(verbose_name="Is Featured?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")
    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created_at', )

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name="Is Active?") # for activating and deactivating a products color

    def __str__(self):
        return f"{self.product.name} - {self.color.name}"
    
class ProductImage(models.Model):
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    # Add other fields like image captions, etc.

    def __str__(self):
        return f"{self.product_color} - Image"

class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    locality = models.CharField(max_length=150, verbose_name="Nearest Location")
    city = models.CharField(max_length=150, verbose_name="City")
    state = models.CharField(max_length=150, verbose_name="State")

    def __str__(self):
        return self.locality

STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled')
)
class Order(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Order ID")
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    address = models.ForeignKey(Address, verbose_name="Shipping Address", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem', verbose_name="Products")
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Ordered Date")
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=50,
        default="Pending"
    )
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Quantity")

# Table for product review
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()  # You can use a RatingField if available
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} Review"