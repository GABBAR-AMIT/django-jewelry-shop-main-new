from django.urls import path
from . import views


urlpatterns = [
    path('login', views.custom_superuser_login, name='custom_login'), # for login
    path('dash', views.ahome, name='custom_admin_dashboard'), # for home
    path('products/', views.list_products, name='list_products'), # for product view
    path('products/create/', views.create_product, name='create_product'), # for adding product
    path('products/edit/<int:product_id>/<int:pc_id>', views.edit_product, name='edit_product'), # for editing the product
    path('delimg/<int:pk>/<int:pid>/<int:pc_id>', views.delimg, name='delimg'), # to delete the images from the edit page 
    path('products/delete/<int:product_id>', views.delete_product, name='delete_product'), # for deleting the product
    path('all_orders/', views.all_orders, name='all_orders'), # to see all the orders.
]
