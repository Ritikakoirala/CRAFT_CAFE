"""
Craft Cafe — Views
All views with integrated real-time email notifications.
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg
from .models import Category, Product, Order, OrderItem, Payment, Feedback
from .email_service import (
    send_order_confirmation,
    send_order_status_update,
    send_new_order_admin_alert,
    send_contact_message,
    send_feedback_thank_you,
)

logger = logging.getLogger(__name__)


def is_admin(user):
    return user.is_staff


# ── Cart helpers ─────────────────────────────────────────────────────────────
def get_cart(request):
    return request.session.get('cart', {})


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


# ── Public pages ──────────────────────────────────────────────────────────────
def home(request):
    featured = Product.objects.filter(is_featured=True, is_available=True)[:6]
    feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:6]
    top_rated = Product.objects.filter(is_available=True).annotate(
        avg_rating=Avg('feedback__rating')).order_by('-avg_rating')[:4]
    categories = Category.objects.all()
    return render(request, 'cafe/home.html', {
        'featured': featured,
        'feedbacks': feedbacks,
        'top_rated': top_rated,
        'categories': categories,
    })


def menu(request):
    categories = Category.objects.all()
    selected_cat = request.GET.get('category', 'all')
    if selected_cat == 'all':
        products = Product.objects.filter(is_available=True).select_related('category')
    else:
        products = Product.objects.filter(
            is_available=True, category__slug=selected_cat
        ).select_related('category')
    return render(request, 'cafe/menu.html', {
        'categories': categories,
        'products': products,
        'selected_cat': selected_cat,
    })


def cart(request):
    cart_data = get_cart(request)
    cart_items, total = _build_cart_items(cart_data)
    return render(request, 'cafe/cart.html', {'cart_items': cart_items, 'total': total})


def _build_cart_items(cart_data):
    cart_items = []
    total = 0
    for pid, item in cart_data.items():
        try:
            product = Product.objects.get(id=int(pid))
            subtotal = product.price * item['qty']
            cart_items.append({'product': product, 'qty': item['qty'], 'subtotal': subtotal})
            total += subtotal
        except Product.DoesNotExist:
            pass
    return cart_items, total


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_data = get_cart(request)
    pid = str(product_id)
    if pid in cart_data:
        cart_data[pid]['qty'] += 1
    else:
        cart_data[pid] = {'qty': 1, 'name': product.name, 'price': str(product.price)}
    save_cart(request, cart_data)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count = sum(v['qty'] for v in cart_data.values())
        return JsonResponse({'success': True, 'cart_count': count})
    messages.success(request, f'{product.name} added to cart!')
    return redirect('menu')


@require_POST
def update_cart(request, product_id):
    cart_data = get_cart(request)
    pid = str(product_id)
    qty = int(request.POST.get('qty', 1))
    if qty <= 0:
        cart_data.pop(pid, None)
    else:
        if pid in cart_data:
            cart_data[pid]['qty'] = qty
    save_cart(request, cart_data)
    return redirect('cart')


@require_POST
def remove_from_cart(request, product_id):
    cart_data = get_cart(request)
    cart_data.pop(str(product_id), None)
    save_cart(request, cart_data)
    return redirect('cart')


def checkout(request):
    cart_data = get_cart(request)
    if not cart_data:
        messages.warning(request, 'Your cart is empty!')
        return redirect('menu')

    cart_items, total = _build_cart_items(cart_data)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        notes = request.POST.get('notes', '')
        payment_method = request.POST.get('payment_method', 'cod')
        reference_id = request.POST.get('reference_id', '')

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            delivery_address=address,
            notes=notes,
            total_amount=total,
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['qty'],
                price=item['product'].price,
            )

        payment = Payment(order=order, payment_method=payment_method, reference_id=reference_id)
        if 'screenshot' in request.FILES:
            payment.screenshot = request.FILES['screenshot']
        payment.save()

        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True

        # ── Send emails immediately ──────────────────────────
        try:
            send_order_confirmation(order)          # → customer
            send_new_order_admin_alert(order)       # → cafe owner
        except Exception as e:
            logger.error(f"Post-order email error: {e}")
        # ────────────────────────────────────────────────────

        messages.success(request, f'Order #{order.id} placed! Confirmation sent to {email}')
        return redirect('order_success', order_id=order.id)

    return render(request, 'cafe/checkout.html', {'cart_items': cart_items, 'total': total})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'cafe/order_success.html', {'order': order})


def order_track(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'cafe/order_track.html', {'order': order})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        msg = request.POST.get('message', '').strip()
        if name and email and msg:
            try:
                send_contact_message(name, email, msg)
                messages.success(request, f'Message sent! We\'ll reply to {email} within 24 hours.')
            except Exception as e:
                logger.error(f"Contact email error: {e}")
                messages.warning(request, 'Message received! We\'ll get back to you soon.')
        else:
            messages.error(request, 'Please fill in all fields.')
        return redirect('contact')
    return render(request, 'cafe/contact.html')


def submit_feedback(request):
    if request.method == 'POST':
        name = request.POST.get('reviewer_name', 'Anonymous')
        rating = int(request.POST.get('rating', 5))
        message = request.POST.get('message', '')
        email = request.POST.get('email', '').strip()
        order_id = request.POST.get('order_id')
        order = None
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                pass

        Feedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            reviewer_name=name,
            rating=rating,
            message=message,
            order=order,
        )

        # ── Send thank-you email if email provided ────────────
        if email:
            try:
                send_feedback_thank_you(name, email)
            except Exception as e:
                logger.error(f"Feedback email error: {e}")
        # ──────────────────────────────────────────────────────

        messages.success(request, 'Thank you for your feedback! ⭐')
        return redirect('home')
    return render(request, 'cafe/feedback.html')


# ── Auth ──────────────────────────────────────────────────────────────────────
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created! Welcome to Craft Cafe!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# ── Admin Dashboard ───────────────────────────────────────────────────────────
@user_passes_test(is_admin)
def admin_dashboard(request):
    orders = Order.objects.order_by('-created_at')[:10]
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    feedbacks = Feedback.objects.order_by('-created_at')[:5]
    return render(request, 'admin_panel/dashboard.html', {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'feedbacks': feedbacks,
    })


@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.order_by('-created_at').select_related('payment')
    return render(request, 'admin_panel/orders.html', {'orders': orders})


@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status and status != order.status:
            order.status = status
            order.save()
            # ── Email customer on status change ──────────────
            if status in ('preparing', 'on_the_way', 'delivered', 'cancelled'):
                try:
                    send_order_status_update(order)
                    messages.success(request, f'Status updated & customer notified via email.')
                except Exception as e:
                    logger.error(f"Status email error: {e}")
                    messages.success(request, 'Order status updated!')
            else:
                messages.success(request, 'Order status updated!')
            # ─────────────────────────────────────────────────

        pay_status = request.POST.get('payment_status')
        if pay_status and hasattr(order, 'payment'):
            order.payment.payment_status = pay_status
            order.payment.save()
            messages.success(request, 'Payment status updated!')

        return redirect('admin_order_detail', order_id=order_id)
    return render(request, 'admin_panel/order_detail.html', {'order': order})


@user_passes_test(is_admin)
def admin_products(request):
    products = Product.objects.select_related('category').order_by('category', 'name')
    categories = Category.objects.all()
    return render(request, 'admin_panel/products.html', {'products': products, 'categories': categories})


@user_passes_test(is_admin)
def admin_product_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        Product.objects.create(
            name=request.POST['name'],
            description=request.POST.get('description', ''),
            price=request.POST['price'],
            category_id=request.POST['category'],
            is_available=bool(request.POST.get('is_available')),
            is_featured=bool(request.POST.get('is_featured')),
            image=request.FILES.get('image'),
        )
        messages.success(request, 'Product added!')
        return redirect('admin_products')
    return render(request, 'admin_panel/product_form.html', {'categories': categories, 'action': 'Add'})


@user_passes_test(is_admin)
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST.get('description', '')
        product.price = request.POST['price']
        product.category_id = request.POST['category']
        product.is_available = bool(request.POST.get('is_available'))
        product.is_featured = bool(request.POST.get('is_featured'))
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated!')
        return redirect('admin_products')
    return render(request, 'admin_panel/product_form.html', {
        'product': product, 'categories': categories, 'action': 'Edit'
    })


@user_passes_test(is_admin)
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect('admin_products')


@user_passes_test(is_admin)
def admin_feedback(request):
    feedbacks = Feedback.objects.order_by('-created_at')
    return render(request, 'admin_panel/feedback.html', {'feedbacks': feedbacks})


@user_passes_test(is_admin)
def admin_feedback_delete(request, feedback_id):
    fb = get_object_or_404(Feedback, id=feedback_id)
    fb.delete()
    messages.success(request, 'Feedback deleted!')
    return redirect('admin_feedback')
