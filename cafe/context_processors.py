def cart_count(request):
    cart = request.session.get('cart', {})
    count = sum(v.get('qty', 0) for v in cart.values())
    return {'cart_count': count}
