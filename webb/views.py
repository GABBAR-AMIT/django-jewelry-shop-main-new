from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product, Color, ProductImage, Category, Order, ProductColor
from django.contrib import messages
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test # for super user authentication
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse

#admin home 
@user_passes_test(lambda user: user.is_superuser)
def ahome(request):
    #sales as per the day, week, month and year
    # Total sales for the current day
    today = timezone.now()
    total_sales_day = calculate_total_sales(today, today + timedelta(days=1))

    # Total sales for the current week
    current_week = today.date().isocalendar()[1]
    total_sales_week = calculate_total_sales(today, today - timedelta(days=current_week))

    # Total sales for the current month
    total_sales_month = calculate_total_sales(today, today - timedelta(days=today.day))

    # Total sales for the current year
    total_sales_year = calculate_total_sales(today, today - timedelta(days=365))

    return render(request, 'adash.html', {'day': total_sales_day, 'week': total_sales_week, 'month': total_sales_month, 'year': total_sales_year})

def calculate_total_sales(start_date, end_date):
    orders = Order.objects.filter(ordered_date__range=(start_date, end_date))
    total_sales = orders.aggregate(total=Sum('orderitem__product__price'))['total']
    return total_sales or 0


# to add the product
@user_passes_test(lambda user: user.is_superuser)
def create_product(request):
    # Retrieve the categories for the product form dropdown
    categories = Category.objects.all()
    colors=Color.objects.all()
    if request.method == 'POST':
        if 'title' in request.POST: # Get product details from the form            
            title = request.POST.get('title')
            existing_product = Product.objects.filter(name=title).first()

            if existing_product:
                # Product already exists, retrieve the existing product
                product = existing_product
            else:
                # Product does not exist, create a new one
                price = request.POST.get('price')
                description = request.POST.get('description')
                slug = request.POST.get('slug')
                sku = request.POST.get('sku')
                short_description = request.POST.get('short_description')
                detail_description = request.POST.get('detail_description')
                is_active = request.POST.get('is_active') == 'on'
                is_featured = request.POST.get('is_featured') == 'on'

                # Get the selected category from the form
                category_id = request.POST.get('category')
                category = Category.objects.get(id=category_id)  # Assuming you have a Category model

                # Create a new product
                product = Product.objects.create(
                    name=title,
                    price=price,
                    description=description,
                    slug=slug,
                    sku=sku,
                    short_description=short_description,
                    detail_description=detail_description,
                    is_active=is_active,
                    is_featured=is_featured,
                    category=category  # Set the category for the product
                    # Add more fields as needed
                )
                product.save()
                # Handle product colors and images
            for color_name in request.POST.getlist('color_name'):
                color= Color.objects.get(id=color_name)
                product_color = ProductColor(product=product, color=color)
                product_color.save()

                for image in request.FILES.getlist(f'images'):
                    product_image = ProductImage(product_color=product_color, image=image)
                    product_image.save()

            # Redirect to a success page or any other desired action
            messages.success(request, "Product created successfully.")
            return render(request, 'test.html',{'categories': categories,'colors':colors})
            
            # return HttpResponse("Product created successfully.")

        if 'name' in request.POST: # Get category details from the form            
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active') == 'on'
            is_featured = request.POST.get('is_featured') == 'on'

            # Handle category image
            category_image = request.FILES.get('category_image')

            # Create a new category
            category = Category.objects.create(
                name=name,
                slug=slug,
                description=description,
                is_active=is_active,
                is_featured=is_featured,
                image=category_image  # Set the category image
                # Add more fields as needed
            )

            # Redirect to a success page or any other desired action
            messages.success(request, "Category created successfully.")
            return render(request, 'test.html', {'categories': categories})
            # return HttpResponse("Category created successfully.")

        if 'colorname' in request.POST: # for getting the colors
                    colorname = request.POST['colorname']
                    color=Color.objects.create(name=colorname)
                    color.save()  

    return render(request, 'test.html', {'categories': categories, 'colors':colors})

# admin list of all the products
@user_passes_test(lambda user: user.is_superuser)
def list_products(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

#admin edit of products
@user_passes_test(lambda user: user.is_superuser)
def edit_product(request, product_id, pc_id):
    categories = Category.objects.all()
    
    product = get_object_or_404(Product, id=product_id) # Retrieve the product object from the database
    # need product color id to get the specific product color
    product_colors = get_object_or_404(ProductColor, id=pc_id)
    if request.method == 'POST':
        # Extract data from the form for Product model
        product.name = request.POST.get('title')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.slug = request.POST.get('slug')
        product.sku = request.POST.get('sku')
        product.short_description = request.POST.get('short_description')
        product.detail_description = request.POST.get('detail_description')
        # product.is_active = request.POST.get('is_active') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'

        # Save the changes to the product
        product.save()

        # product_color=request.POST.get('color_name')
        
        product_colors.is_active = request.POST.get('is_active') == '1'
        product_colors.save()
        # print(existing_product_color)
        # if existing_product_color:
        for image in request.FILES.getlist(f'images'):
                product_image = ProductImage(product_color=product_colors, image=image)
                product_image.save()
        return redirect('list_products')  # Redirect to the product list page or any desired page

    return render(request, 'edit_product.html', {'product': product, 'category':categories, 'productcolor':product_colors})

def delimg(request, pk, pid, pc_id):
    img=ProductImage.objects.get(id=pk)
    img.delete()
    
    return redirect('edit_product', product_id=pid, pc_id=pc_id)
# admin delete product
@user_passes_test(lambda user: user.is_superuser)
def delete_product(request, product_id):
    # Retrieve the product object from the database
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('list_products')  # Redirect to the product list page or any desired page

#admin see all the orders 
@user_passes_test(lambda user: user.is_superuser)
def all_orders(request):
    all_orders = Order.objects.all()
    for order in all_orders:
        total_price = sum(order_item.product.price * order_item.quantity for order_item in order.orderitem_set.all())
        order.total_price = total_price  # Add the total price to the order instance
    if request.method =="POST":
        # Get the selected start and end dates from the form
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        # Parse the date strings into datetime objects
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime(2000, 1, 1)  # A default start date if not provided

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime(2100, 12, 31)  # A default end date if not provided

        # Filter orders based on the date range
        filtered_orders = Order.objects.filter(ordered_date__range=(start_date, end_date))

        return render(request, 'all_orders.html', {'orders': filtered_orders})
    return render(request, 'all_orders.html', {'orders': all_orders})

# Admin Login
def custom_superuser_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Manually authenticate the superuser
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            # Log in the superuser
            login(request, user)
            return redirect('custom_admin_dashboard')  # Redirect to the custom admin dashboard URL

    return render(request, 'custom_login.html')


#adding categories and colors 
@user_passes_test(lambda user: user.is_superuser)
def catcol(request):
    pass