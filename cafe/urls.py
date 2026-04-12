from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('order/track/<int:order_id>/', views.order_track, name='order_track'),
    path('contact/', views.contact, name='contact'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Admin Panel
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('dashboard/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('dashboard/products/', views.admin_products, name='admin_products'),
    path('dashboard/products/add/', views.admin_product_add, name='admin_product_add'),
    path('dashboard/products/edit/<int:product_id>/', views.admin_product_edit, name='admin_product_edit'),
    path('dashboard/products/delete/<int:product_id>/', views.admin_product_delete, name='admin_product_delete'),
    path('dashboard/feedback/', views.admin_feedback, name='admin_feedback'),
    path('dashboard/feedback/delete/<int:feedback_id>/', views.admin_feedback_delete, name='admin_feedback_delete'),
]
