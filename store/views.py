import django
from django.contrib.auth.models import User
from store.models import Cart
from webb.models import Category, Product, ProductImage, Order, Address,ProductColor, ProductReview
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # for pagination 
from decimal import Decimal  # Import Decimal for handling currency values


# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.select_related('category').prefetch_related('productcolor_set__productimage_set').filter(is_active=True, is_featured=True)[:8]
    context = {
        'categories': categories,
        'products': products,
    }
    print(categories)
    return render(request, 'store/index.html', context)


def detail(request, slug, pc_id):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    product = get_object_or_404(Product, slug=slug)
    product_color=ProductColor.objects.get(id=pc_id)
    pcolor=ProductColor.objects.filter(product=product)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    review = ProductReview.objects.filter(product=product)
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
        review = ProductReview.objects.create(
                        user=user,
                        product=product,
                        rating=rating,
                        review_text=review_text
                    )
        return redirect('product_detail', slug=slug, pc_id=pc_id)
    context = {
        'categories': categories,
        'product': product,
        'related_products': related_products,
        'pcolor': product_color,
        'productcolor':pcolor,
        'review':review

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    # products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)
    ########## Slider ################
    # Get the price range from the request parameters
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 2000)

    # Validate and convert the price range values to Decimal
    try:
        min_price = Decimal(min_price)
        max_price = Decimal(max_price)
    except (ValueError, TypeError):
        # Handle invalid values (non-numeric, etc.)
        min_price = 0
        max_price = 2000

    # Filter products based on the category and price range
    products = Product.objects.filter(
        is_active=True,
        category=category,
        price__range=(min_price, max_price)
    )
    # Handle sorting
    sorting_option = request.GET.get('sorting', 'default')
    if sorting_option == 'low-high':
        products = products.order_by('price')
    elif sorting_option == 'high-low':
        products = products.order_by('-price')
    ####### Logic for Pagination #######
    products_per_page = 6
    paginator = Paginator(products, products_per_page)
    page = request.GET.get('page')
    try:
        paginated_products = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        paginated_products = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        paginated_products = paginator.page(paginator.num_pages)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'paginated_products': paginated_products,
        'min_price': min_price,  # Add min_price to the context for updating the slider
        'max_price': max_price,
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id') # pc_id
    # product = get_object_or_404(Product, id=product_id)
    product_color = ProductColor.objects.get(id=product_id)
    product = product_color.product
    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product, product_color=product_color, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product, product_color=product_color, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product, product_color=product_color).save()
    
    return redirect('store:cart')


@login_required
def cart(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'categories': categories,
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')


@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')
    
    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect('store:orders')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})





def shop(request):
    return render(request, 'store/shop.html')


def test(request):
    return render(request, 'store/test.html')
